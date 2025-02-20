import os
import re
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file, flash, session
from PIL import Image
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

appV5 = Flask(__name__)
appV5.secret_key = "sua_chave_secreta_aqui"  # Required for flash messages

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

def get_cover_image(folder_path):
    """Get the cover image for the folder."""
    cover_filenames = ["cover.jpg", "cover.png", "cover.webp"]
    
    for filename in cover_filenames:
        cover_path = os.path.join(folder_path, filename)
        if os.path.exists(cover_path):
            # Replace backslashes with forward slashes for URLs
            return url_for('cover_image', filename=os.path.join(os.path.basename(folder_path), filename).replace("\\", "/"))
    
    return None

@appV5.route("/")
def index():
    # Lista os PDFs disponíveis na pasta de quadrinhos
    arquivos_pdf = [f for f in os.listdir(caminho_pasta) if f.endswith('.pdf')]
    return render_template("index.html", comics=arquivos_pdf)

@appV5.route("/processar_url", methods=["POST"])
def processar_url():
    url_site = request.form["url_site"].strip()
    num_capitulos = int(request.form["num_capitulos"])
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # Extrair o nome do mangá e o número do capítulo inicial
    parsed_url = urlparse(url_site)
    path_parts = parsed_url.path.split("/")
    manga_name = path_parts[2] if len(path_parts) > 2 else "manga"

    # Verifica o formato da URL para extrair o número do capítulo
    if len(path_parts) > 3:
        chapter_part = path_parts[3]  # Pode ser "capitulo-XX" ou apenas "XX"
        if chapter_part.startswith("capitulo-"):
            # Formato 1: "capitulo-XX"
            start_chapter = int(chapter_part.split("-")[-1])  # Extrai o número (e.g., "11")
        else:
            # Formato 2: "XX"
            start_chapter = int(chapter_part)  # Extrai o número diretamente
    else:
        start_chapter = 0  # Default to 0 if no number is found

    # Verifica se existe um subdiretório com o nome do mangá
    manga_dir = os.path.join(caminho_pasta, manga_name)
    if not os.path.exists(manga_dir):
        os.makedirs(manga_dir)  # Cria o subdiretório se não existir
        print(f"Subdiretório criado: {manga_dir}")

    # Loop para baixar os capítulos
    for i in range(num_capitulos):
        chapter_number = start_chapter + i

        # Gera a URL do capítulo com base no formato original
        if "capitulo-" in url_site:
            # Formato 1: Substitui "capitulo-XX" pelo número do capítulo atual
            chapter_url = url_site.replace(f"capitulo-{start_chapter}", f"capitulo-{chapter_number}")
        else:
            # Formato 2: Substitui "/XX/" pelo número do capítulo atual
            chapter_url = url_site.replace(f"/{start_chapter}/", f"/{chapter_number}/")

        # Faz o request para o site
        try:
            print(f"Acessando o site: {chapter_url}")
            response = requests.get(chapter_url, headers=headers)
            response.raise_for_status()
            print(f"Status da requisição: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar o site: {e}")
            flash(f"Erro ao acessar o capítulo {chapter_number}.", "error")
            continue

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
                img_url = urljoin(chapter_url, img_url)
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
            [f for f in os.listdir(pasta_imagens) if f.lower().endswith(('.jpg', '.webp', '.png'))],
            key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0  # Ordena numericamente pelo número extraído do nome
        )

        if not arquivos:
            flash(f"Nenhuma imagem válida (.jpg ou .webp) encontrada no capítulo {chapter_number}.", "error")
            continue

        # Carrega as imagens para serem convertidas
        imagens = []
        for arquivo in arquivos:
            try:
                imagem = Image.open(os.path.join(pasta_imagens, arquivo)).convert("RGB")
                imagens.append(imagem)
            except Exception as e:
                flash(f"Erro ao carregar a imagem {arquivo}: {e}", "error")
                continue

        # Verifica se há imagens válidas para salvar
        if not imagens:
            flash(f"Nenhuma imagem válida foi carregada no capítulo {chapter_number}.", "error")
            continue

        # Define o caminho completo do PDF
        nome_pdf = f"{manga_name} {chapter_number}.pdf"
        caminho_completo_pdf = os.path.join(manga_dir, nome_pdf)  # Salva o PDF no subdiretório do mangá

        # Salvar em PDF
        imagens[0].save(caminho_completo_pdf, save_all=True, append_images=imagens[1:])
        print(f"PDF '{nome_pdf}' criado com sucesso em '{manga_dir}'!")

        # Limpar as imagens após criar o PDF
        for arquivo in arquivos:
            try:
                os.remove(os.path.join(pasta_imagens, arquivo))
                print(f"Arquivo '{arquivo}' removido com sucesso.")
            except Exception as e:
                print(f"Erro ao tentar remover o arquivo '{arquivo}': {e}")

        flash(f"PDF '{nome_pdf}' gerado com sucesso!", "success")

    return redirect(url_for("index"))

@appV5.route("/biblioteca")
def biblioteca():
    conteudo = []
    for item in os.listdir(caminho_pasta):
        item_caminho = os.path.join(caminho_pasta, item)
        if os.path.isdir(item_caminho):
            cover_image = get_cover_image(item_caminho)
            conteudo.append({"nome": item, "tipo": "pasta", "cover_image": cover_image})

    # Debug print to verify the conteudo list
    print(f"Conteudo: {conteudo}")

    return render_template("biblioteca.html", conteudo=conteudo, nome_pasta=None)

@appV5.route("/visualizar/<path:caminho_relativo>")
def visualizar_pdf(caminho_relativo):
    caminho_pdf = os.path.join(caminho_pasta, caminho_relativo)

    # Normaliza o caminho e verifica se ele existe
    caminho_pdf = os.path.normpath(caminho_pdf)

    # Evitar problemas de segurança (acesso fora da pasta raiz)
    if not caminho_pdf.startswith(os.path.abspath(caminho_pasta)):
        return "Acesso negado.", 403

    if not os.path.isfile(caminho_pdf):
        return f"PDF não encontrado: {caminho_pdf}", 404

    # Extrai o nome da pasta (subdiretório) do caminho_relativo
    nome_pasta = os.path.dirname(caminho_relativo)

    # Salva o caminho do último PDF lido na sessão para a pasta específica
    if "last_read" not in session or not isinstance(session["last_read"], dict):
        session["last_read"] = {}  # Garante que seja um dicionário

    session["last_read"][nome_pasta] = caminho_relativo
    session.modified = True  # Garante que a sessão seja salva

    print(f"Last read PDF for folder '{nome_pasta}' saved in session: {caminho_relativo}")  # Debug print

    return send_file(caminho_pdf)

@appV5.route("/biblioteca/<nome_pasta>")
def listar_pasta(nome_pasta):
    caminho_completo = os.path.join(caminho_pasta, nome_pasta)
    if not os.path.exists(caminho_completo):
        return "Pasta não encontrada.", 404

    # List all PDFs in the subdirectory
    arquivos_pdf = [f for f in os.listdir(caminho_completo) if f.endswith('.pdf')]
    conteudo = [{"nome": f, "tipo": "arquivo", "caminho": os.path.join(nome_pasta, f)} for f in arquivos_pdf]

    # Pass the last read PDF information for the specific folder to the template
    last_read = None
    if "last_read" in session and nome_pasta in session["last_read"]:
        last_read = os.path.normpath(session["last_read"][nome_pasta])  # Normalize the last_read path
    print(f"Last read PDF for folder '{nome_pasta}' retrieved from session: {last_read}")  # Debug print

    return render_template("biblioteca.html", conteudo=conteudo, nome_pasta=nome_pasta, last_read=last_read)

@appV5.route('/covers/<path:filename>')
def cover_image(filename):
    return send_from_directory(caminho_pasta, filename)

if __name__ == "__main__":
    appV5.run(debug=True)