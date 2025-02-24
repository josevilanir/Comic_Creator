import os
import re
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file, flash, session
from PIL import Image
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename


appV6 = Flask(__name__)
appV6.secret_key = "sua_chave_secreta_aqui"  # Required for flash messages

# Define o diretório base na pasta "Comics" dentro da home do usuário
base_dir = os.path.join(os.path.expanduser("~"), "Comics")
os.makedirs(base_dir, exist_ok=True)  # Garante que a pasta exista

# Caminho para salvar os PDFs gerados
caminho_pasta = base_dir

# Diretório das imagens temporárias
pasta_imagens = os.path.join(os.path.expanduser("~"), "COMIC_CREATOR", "Images")
os.makedirs(pasta_imagens, exist_ok=True)  # Garante que a pasta exista

def get_cover_image(folder_path):
    """Retorna a capa de uma pasta, buscando por um arquivo cover.webp (ou cover.jpg/png como fallback)."""
    cover_filenames = ["cover.webp", "cover.jpg", "cover.png"]
    
    for filename in cover_filenames:
        cover_path = os.path.join(folder_path, filename)
        if os.path.exists(cover_path):
            return url_for('cover_image', filename=os.path.join(os.path.basename(folder_path), filename).replace("\\", "/"))
    
    return "/static/default_thumbnail.jpg"  # Fallback se não houver capa


@appV6.route("/")
def index():
    # Lista os PDFs disponíveis na pasta de quadrinhos
    arquivos_pdf = [f for f in os.listdir(caminho_pasta) if f.endswith('.pdf')]
    return render_template("index.html", comics=arquivos_pdf)

@appV6.route("/processar_url", methods=["POST"])
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

        elif chapter_part.startswith("chap-"):
            # Formato 2: "chap-XX"
            start_chapter = int(chapter_part.split("-")[-1])  # Extrai o número (e.g., "11")

        else:
            # Formato 3: "XX"
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

        if "chap-" in url_site:
            # Formato 2: Substitui "chap-XX" pelo número do capítulo atual
            chapter_url = url_site.replace(f"chap-{start_chapter}", f"chap-{chapter_number}")
        
        else:
            # Formato 3: Substitui "/XX/" pelo número do capítulo atual
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

from PIL import Image
import fitz  # PyMuPDF
import os

def generate_pdf_thumbnail(pdf_path, thumbnail_path):
    """Gera uma thumbnail do PDF, reduzindo a qualidade para carregamento mais rápido."""
    if os.path.exists(thumbnail_path):  
        print(f"🔄 Thumbnail já existe: {thumbnail_path}")
        return True  # Evita recriação

    try:
        print(f"📄 Gerando thumbnail para: {pdf_path}")
        doc = fitz.open(pdf_path)  # Abre o PDF
        page = doc[3]  # Pega a primeira página
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Renderiza a página
        
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)  # Garante que a pasta exista
        
        # Converte Pixmap para um objeto de imagem do Pillow
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Salva a imagem em JPEG reduzindo a qualidade
        img.save(thumbnail_path, "JPEG", quality=50)  # Agora funciona corretamente!
        
        print(f"✅ Thumbnail salva: {thumbnail_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar thumbnail para {pdf_path}: {e}")
    
    return False

@appV6.route("/biblioteca")
def biblioteca():
    conteudo = []
    for item in os.listdir(caminho_pasta):
        item_caminho = os.path.join(caminho_pasta, item)

        if os.path.isdir(item_caminho):  # É uma pasta
            cover_image = get_cover_image(item_caminho)
            conteudo.append({"nome": item, "tipo": "pasta", "cover_image": cover_image})
        elif item.endswith(".pdf"):  # É um PDF
            thumbnail_filename = f"{os.path.splitext(item)[0]}.jpg"
            thumbnail_path = os.path.join("static", "thumbnails", thumbnail_filename)

            if not os.path.exists(thumbnail_path):  # Gera se estiver faltando
                success = generate_pdf_thumbnail(item_caminho, thumbnail_path)
                if not success:
                    thumbnail_path = "/static/default_thumbnail.jpg"

            thumbnail_url = url_for("static", filename=f"thumbnails/{thumbnail_filename}")
            conteudo.append({"nome": item, "tipo": "arquivo", "caminho": item, "thumbnail": thumbnail_url})

    return render_template("biblioteca.html", conteudo=conteudo, nome_pasta=None)


@appV6.route("/visualizar/<path:caminho_relativo>")
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

@appV6.route("/biblioteca/<nome_pasta>")
def listar_pasta(nome_pasta):
    caminho_completo = os.path.join(caminho_pasta, nome_pasta)
    if not os.path.exists(caminho_completo):
        return "Pasta não encontrada.", 404

    # Lista os PDFs dentro da pasta
    arquivos_pdf = [f for f in os.listdir(caminho_completo) if f.endswith('.pdf')]
    conteudo = []

    for pdf in arquivos_pdf:
        pdf_path = os.path.join(caminho_completo, pdf)
        thumbnail_filename = f"{nome_pasta}_{os.path.splitext(pdf)[0]}.jpg"
        thumbnail_path = os.path.join("static", "thumbnails", thumbnail_filename)

        # Gera a thumbnail se não existir
        if not os.path.exists(thumbnail_path):
            success = generate_pdf_thumbnail(pdf_path, thumbnail_path)
            if not success:
                thumbnail_path = "/static/default_thumbnail.jpg"

        thumbnail_url = url_for("static", filename=f"thumbnails/{thumbnail_filename}")
        conteudo.append({"nome": pdf, "tipo": "arquivo", "caminho": os.path.join(nome_pasta, pdf), "thumbnail": thumbnail_url})

    return render_template("biblioteca.html", conteudo=conteudo, nome_pasta=nome_pasta)

@appV6.route('/covers/<path:filename>')
def cover_image(filename):
    return send_from_directory(caminho_pasta, filename)

@appV6.route("/upload_capa/<nome_pasta>", methods=["POST"])
def upload_capa(nome_pasta):
    """Permite o upload de uma nova capa para uma subpasta."""
    if "capa" not in request.files:
        flash("Nenhum arquivo enviado.", "error")
        return redirect(request.referrer)

    file = request.files["capa"]
    
    if file.filename == "":
        flash("Arquivo inválido.", "error")
        return redirect(request.referrer)

    # Caminho da pasta de destino
    pasta_destino = os.path.join(caminho_pasta, nome_pasta)
    if not os.path.exists(pasta_destino):
        flash("Pasta não encontrada.", "error")
        return redirect(request.referrer)

    # Define o nome do arquivo de capa (sempre "cover.webp")
    filename = "cover.webp"
    caminho_capa = os.path.join(pasta_destino, filename)

    try:
        file.save(caminho_capa)
        flash("Capa atualizada com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao salvar a capa: {e}", "error")

    return redirect(request.referrer)

if __name__ == "__main__":
    appV6.run(debug=True)