import os
import re
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

appV4 = Flask(__name__)

# Caminho para salvar o PDF gerado
caminho_pasta = "C:/Users/vilan/Comics"
# Certifica que a pasta existe
if not os.path.isdir(caminho_pasta):
    os.makedirs(caminho_pasta)

# Diretório das imagens
pasta_imagens = "C:/Users/vilan/COMIC_CREATOR/Images"
# Certifica que o diretório de imagens existe
if not os.path.exists(pasta_imagens):
    os.makedirs(pasta_imagens)

@appV4.route("/")
def index():
    return render_template("index.html")

@appV4.route("/baixar_imagens", methods=["POST"])
def baixar_imagens():
    url_site = request.form["url_site"].strip()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # Faz o request para o site
    try:
        print(f"Acessando o site: {url_site}")
        response = requests.get(url_site, headers=headers)
        response.raise_for_status()
        print(f"Status da requisição: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o site: {e}")
        return "Erro ao acessar o site.", 400

    # Parseia o conteúdo HTML do site
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontra todas as tags <img> no HTML
    tags_imagens = soup.find_all('img')
    print(f"Total de tags <img> encontradas: {len(tags_imagens)}")

    def obter_url_imagem(tag):
        """Tenta obter uma URL válida da tag de imagem"""
        # Prioriza 'src', mas verifica 'data-src' ou 'data-lazy' se necessário
        for atributo in ['src', 'data-src', 'data-lazy']:
            url = tag.get(atributo)
            if url and not url.startswith("data:"):
                return url
        return None

    # Baixa as imagens filtradas
    for img in tags_imagens:
        img_url = obter_url_imagem(img)
        if img_url:
            img_url = urljoin(url_site, img_url)
            print(f"Processando imagem: {img_url}")
            if img_url.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
                try:
                    print(f"Baixando imagem: {img_url}")
                    img_data = requests.get(img_url, headers=headers).content
                    nome_arquivo = os.path.basename(img_url.split("?")[0])
                    caminho_completo = os.path.join(pasta_imagens, nome_arquivo)
                    with open(caminho_completo, 'wb') as arquivo:
                        arquivo.write(img_data)
                    print(f"Imagem salva: {nome_arquivo}")
                except Exception as e:
                    print(f"Erro ao baixar {img_url}: {e}")
        else:
            print("Tag <img> sem URL válida encontrada.")

    return "Imagens baixadas com sucesso!", 200

@appV4.route("/gerar_cbr", methods=["POST"])
def gerar_pdf():
    nome_pdf = request.form["nome_pdf"].strip() + ".pdf"

    # Verifica se a pasta de imagens existe
    if not os.path.exists(pasta_imagens):
        return "Diretório de imagens não encontrado.", 400

    # Carrega as imagens e ordena, filtra arquivos válidos (.jpg e .webp)
    arquivos = sorted(
        [f for f in os.listdir(pasta_imagens) if f.lower().endswith(('.jpg', '.webp', '.png'))],
        key=lambda x: int(re.search(r'\d+', x).group())  # Ordena numericamente pelo número extraído do nome
    )

    if not arquivos:
        return "Nenhuma imagem válida (.jpg ou .webp) encontrada.", 400

    # Carrega as imagens para serem convertidas
    imagens = []
    for arquivo in arquivos:
        try:
            imagem = Image.open(os.path.join(pasta_imagens, arquivo)).convert("RGB")
            imagens.append(imagem)
        except Exception as e:
            return f"Erro ao carregar a imagem {arquivo}: {e}", 400

    # Verifica se há imagens válidas para salvar
    if not imagens:
        return "Nenhuma imagem válida foi carregada.", 400

    # Define o caminho completo do PDF
    caminho_completo_pdf = os.path.join(caminho_pasta, nome_pdf)

    # Salvar em PDF
    imagens[0].save(caminho_completo_pdf, save_all=True, append_images=imagens[1:])
    print(f"PDF '{nome_pdf}' criado com sucesso em '{caminho_pasta}'!")

    # Limpar as imagens após criar o PDF
    for arquivo in arquivos:
        try:
            os.remove(os.path.join(pasta_imagens, arquivo))
            print(f"Arquivo '{arquivo}' removido com sucesso.")
        except Exception as e:
            print(f"Erro ao tentar remover o arquivo '{arquivo}': {e}")

    return f"PDF '{nome_pdf}' gerado com sucesso!", 200

@appV4.route("/biblioteca")
def biblioteca():
    arquivos_pdf = [f for f in os.listdir(caminho_pasta) if f.endswith('.pdf')]
    return render_template("biblioteca.html", arquivos_pdf=arquivos_pdf)

@appV4.route("/visualizar/<nome_pdf>")
def visualizar_pdf(nome_pdf):
    caminho_pdf = os.path.join(caminho_pasta, nome_pdf)
    if not os.path.exists(caminho_pdf):
        return "PDF não encontrado.", 404
    return send_from_directory(caminho_pasta, nome_pdf)

if __name__ == "__main__":
    appV4.run(debug=True)