import os
import re
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file, flash
from PIL import Image
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

appV4 = Flask(__name__)
appV4.secret_key = "sua_chave_secreta_aqui"  # Required for flash messages

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
    # Lista os PDFs disponíveis na pasta de quadrinhos
    arquivos_pdf = [f for f in os.listdir(caminho_pasta) if f.endswith('.pdf')]
    return render_template("index.html", comics=arquivos_pdf)

@appV4.route("/processar_url", methods=["POST"])
def processar_url():
    url_site = request.form["url_site"].strip()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # Extrair o nome do PDF da URL
    parsed_url = urlparse(url_site)
    path_parts = parsed_url.path.split("/")

    # Extrair o nome do mangá e o número do capítulo
    manga_name = path_parts[2] if len(path_parts) > 2 else "manga"
    chapter_part = path_parts[3] if len(path_parts) > 3 else "capitulo-0"  # Default to "capitulo-0" if not found

    # Extrair o número do capítulo (e.g., "capitulo-80" -> "80")
    if "-" in chapter_part:
        chapter_number = chapter_part.split("-")[-1]  # Extrai o número (e.g., "80")
    else:
        chapter_number = "0"  # Default to "0" if no number is found

    nome_pdf = f"{manga_name} {chapter_number}.pdf"

    # Faz o request para o site
    try:
        print(f"Acessando o site: {url_site}")
        response = requests.get(url_site, headers=headers)
        response.raise_for_status()
        print(f"Status da requisição: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o site: {e}")
        flash("Erro ao acessar o site.", "error")
        return redirect(url_for("index"))

    # Parseia o conteúdo HTML do site
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontra todas as tags <img> no HTML
    tags_imagens = soup.find_all('img')
    print(f"Total de tags <img> encontradas: {len(tags_imagens)}")

    def obter_url_imagem(tag):
        """Tenta obter uma URL válida da tag de imagem"""
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

    # Carrega as imagens e ordena, filtra arquivos válidos (.jpg e .webp)
    arquivos = sorted(
        [f for f in os.listdir(pasta_imagens) if f.lower().endswith(('.jpg', '.webp', '.png', '.jpeg'))],
        key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0  # Ordena numericamente pelo número extraído do nome
    )

    if not arquivos:
        flash("Nenhuma imagem válida (.jpg ou .webp) encontrada.", "error")
        return redirect(url_for("index"))

    # Carrega as imagens para serem convertidas
    imagens = []
    for arquivo in arquivos:
        try:
            imagem = Image.open(os.path.join(pasta_imagens, arquivo)).convert("RGB")
            imagens.append(imagem)
        except Exception as e:
            flash(f"Erro ao carregar a imagem {arquivo}: {e}", "error")
            return redirect(url_for("index"))

    # Verifica se há imagens válidas para salvar
    if not imagens:
        flash("Nenhuma imagem válida foi carregada.", "error")
        return redirect(url_for("index"))

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

    flash(f"PDF '{nome_pdf}' gerado com sucesso!", "success")
    return redirect(url_for("index"))

@appV4.route("/biblioteca")
def biblioteca():
    conteudo = []
    for item in os.listdir(caminho_pasta):
        item_caminho = os.path.join(caminho_pasta, item)
        if os.path.isdir(item_caminho):
            # Add the directory to the conteudo list
            conteudo.append({"nome": item, "tipo": "pasta"})
    return render_template("biblioteca.html", conteudo=conteudo)

@appV4.route("/visualizar/<path:caminho_relativo>")
def visualizar_pdf(caminho_relativo):
    caminho_pdf = os.path.join(caminho_pasta, caminho_relativo)

    # Normaliza o caminho e verifica se ele existe
    caminho_pdf = os.path.normpath(caminho_pdf)

    # Evitar problemas de segurança (acesso fora da pasta raiz)
    if not caminho_pdf.startswith(os.path.abspath(caminho_pasta)):
        return "Acesso negado.", 403

    if not os.path.isfile(caminho_pdf):
        return f"PDF não encontrado: {caminho_pdf}", 404

    return send_file(caminho_pdf)

@appV4.route("/biblioteca/<nome_pasta>")
def listar_pasta(nome_pasta):
    caminho_completo = os.path.join(caminho_pasta, nome_pasta)
    if not os.path.exists(caminho_completo):
        return "Pasta não encontrada.", 404

    arquivos_pdf = [f for f in os.listdir(caminho_completo) if f.endswith('.pdf')]
    return render_template("biblioteca.html", conteudo=[{"nome": f, "tipo": "arquivo", "caminho": os.path.join(nome_pasta, f)} for f in arquivos_pdf], nome_pasta=nome_pasta)

if __name__ == "__main__":
    appV4.run(debug=True)