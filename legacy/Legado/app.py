import os
import requests
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flask import Flask, render_template, request, redirect, url_for, flash

# Configurações do Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Caminho das pastas
PASTA_IMAGENS = "C:/Users/vilan/COMIC_CREATOR/Images"
PASTA_PDF = "C:/Users/vilan/Comics"
os.makedirs(PASTA_IMAGENS, exist_ok=True)

# Função para baixar as imagens
def baixar_imagens(url_site):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # Faz o request para o site
    try:
        print(f"Acessando o site: {url_site}")
        response = requests.get(url_site, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o site: {e}")
        return 0

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
    total_baixadas = 0
    for img in tags_imagens:
        img_url = obter_url_imagem(img)
        if img_url:
            img_url = urljoin(url_site, img_url)
            if img_url.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
                try:
                    img_data = requests.get(img_url, headers=headers).content
                    nome_arquivo = os.path.basename(img_url.split("?")[0])
                    caminho_completo = os.path.join(PASTA_IMAGENS, nome_arquivo)
                    with open(caminho_completo, 'wb') as arquivo:
                        arquivo.write(img_data)
                    total_baixadas += 1
                except Exception as e:
                    print(f"Erro ao baixar {img_url}: {e}")

    return total_baixadas

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para baixar as imagens
@app.route('/baixar_imagens', methods=['POST'])
def processar_download():
    url_site = request.form.get('url_site')

    if not url_site:
        flash("Por favor, insira uma URL válida.", "error")
        return redirect(url_for('index'))

    total_baixadas = baixar_imagens(url_site)

    if total_baixadas > 0:
        flash(f"{total_baixadas} imagens baixadas com sucesso!", "success")
    else:
        flash("Nenhuma imagem válida encontrada no site.", "warning")

    return redirect(url_for('index'))

@app.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    nome_pdf = request.form.get('nome_pdf')

    if not nome_pdf:
        flash("Por favor, insira um nome válido para o PDF.", "error")
        return redirect(url_for('index'))

    nome_pdf += ".pdf"
    caminho_pdf = os.path.join(PASTA_PDF, nome_pdf)

    # Ordena as imagens
    arquivos = sorted([f for f in os.listdir(PASTA_IMAGENS) if f.lower().endswith(('.jpg', '.jpeg', '.webp', '.png'))])
    imagens = []
    for arquivo in arquivos:
        try:
            imagem = Image.open(os.path.join(PASTA_IMAGENS, arquivo)).convert("RGB")
            imagens.append(imagem)
        except Exception as e:
            flash(f"Erro ao carregar a imagem {arquivo}: {e}", "error")
            continue

    if imagens:
        imagens[0].save(caminho_pdf, save_all=True, append_images=imagens[1:])
        flash(f"PDF '{nome_pdf}' criado com sucesso!", "success")

        # Limpa a pasta de imagens
        for arquivo in arquivos:
            try:
                os.remove(os.path.join(PASTA_IMAGENS, arquivo))
                flash(f"Imagem '{arquivo}' removida após gerar o PDF.", "info")
            except Exception as e:
                flash(f"Erro ao remover a imagem '{arquivo}': {e}", "error")
    else:
        flash("Nenhuma imagem encontrada para gerar o PDF.", "warning")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
