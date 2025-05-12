
import os
import re
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urljoin, urlparse
from flask import Flask, request, redirect, url_for, render_template, flash, send_file

app = Flask(__name__)
app.secret_key = "segredo"
BASE_COMICS = os.path.expanduser("~/Comics")
THUMBNAILS = os.path.join("static", "thumbnails")
os.makedirs(BASE_COMICS, exist_ok=True)
os.makedirs(THUMBNAILS, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            flash("URL inválida", "error")
            return redirect(url_for("index"))

        nome_manga, numero_capitulo = extrair_dados_da_url(url)
        if not nome_manga or not numero_capitulo:
            flash("Não foi possível extrair dados da URL", "error")
            return redirect(url_for("index"))

        resultado = baixar_capitulo_para_pdf(url, nome_manga, numero_capitulo)
        if resultado:
            flash(f"PDF salvo em: {resultado}", "success")
        else:
            flash("Nenhuma imagem encontrada.", "error")
        return redirect(url_for("index"))
    return render_template("index.html")

@app.route("/biblioteca")
def biblioteca():
    pastas = []
    for item in os.listdir(BASE_COMICS):
        caminho = os.path.join(BASE_COMICS, item)
        if os.path.isdir(caminho):
            capa_path = os.path.join(caminho, "capa.jpg")
            tem_capa = os.path.exists(capa_path)
            pastas.append({
                "nome": item,
                "tem_capa": tem_capa,
                "capa_url": f"/visualizar/{item}/capa.jpg" if tem_capa else None
            })
    return render_template("biblioteca.html", pastas=pastas)

@app.route("/pasta/<nome_pasta>")
def listar_pasta(nome_pasta):
    pasta = os.path.join(BASE_COMICS, nome_pasta)
    if not os.path.isdir(pasta):
        return "Pasta não encontrada", 404
    arquivos = [f for f in os.listdir(pasta) if f.endswith(".pdf")]
    return render_template("lista_pdfs.html", nome_pasta=nome_pasta, arquivos=arquivos)

@app.route("/visualizar/<manga>/<arquivo>")
def visualizar_pdf(manga, arquivo):
    caminho = os.path.join(BASE_COMICS, manga, arquivo)
    if os.path.exists(caminho):
        return send_file(caminho)
    return "Arquivo não encontrado", 404

@app.route("/upload_capa/<nome_pasta>", methods=["POST"])
def upload_capa(nome_pasta):
    pasta = os.path.join(BASE_COMICS, nome_pasta)
    if not os.path.exists(pasta):
        flash("Pasta não encontrada.", "error")
        return redirect(url_for("biblioteca"))

    if "capa" not in request.files:
        flash("Nenhum arquivo enviado.", "error")
        return redirect(url_for("biblioteca"))

    file = request.files["capa"]
    if file.filename == "":
        flash("Arquivo sem nome.", "error")
        return redirect(url_for("biblioteca"))

    caminho_capa = os.path.join(pasta, "capa.jpg")
    file.save(caminho_capa)
    flash(f"Capa atualizada para {nome_pasta}.", "success")
    return redirect(url_for("biblioteca"))

def extrair_dados_da_url(url):
    parsed = urlparse(url)
    partes = parsed.path.strip("/").split("/")
    try:
        nome_manga = partes[1].replace("-", " ").title()
        capitulo = re.search(r"(\d+)", partes[-1])
        numero = capitulo.group(1) if capitulo else "000"
        return nome_manga, numero
    except IndexError:
        return None, None

def gerar_thumbnail(caminho_pdf, nome_pdf, pasta_manga):
    try:
        doc = fitz.open(caminho_pdf)
        page = doc.load_page(3) if doc.page_count >= 4 else doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        thumb_name = nome_pdf.replace(".pdf", ".jpg")
        caminho_thumb = os.path.join(pasta_manga, thumb_name)
        pix.save(caminho_thumb)
        print(f"✓ Thumbnail salva: {caminho_thumb}")
    except Exception as e:
        print(f"Erro ao gerar thumbnail para {nome_pdf}: {e}")

def baixar_capitulo_para_pdf(url, nome_manga, numero_capitulo):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print("Erro ao acessar a URL:", e)
        return None

    tags = soup.find_all("img")
    imagens = []
    pasta_manga = os.path.join(BASE_COMICS, nome_manga)
    pasta_temp = os.path.join(pasta_manga, "tmp")
    os.makedirs(pasta_temp, exist_ok=True)

    def get_img_url(tag):
        for attr in ["data-src", "data-lazy", "src"]:
            src = tag.get(attr)
            if src and not src.startswith("data:"):
                return urljoin(url, src)
        return None

    for i, tag in enumerate(tags):
        img_url = get_img_url(tag)
        if img_url and img_url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            try:
                nome_img = os.path.join(pasta_temp, f"{str(i).zfill(3)}.jpg")
                img_data = requests.get(img_url, headers=headers).content
                with open(nome_img, "wb") as f:
                    f.write(img_data)
                imagens.append(nome_img)
            except Exception as e:
                print("Erro ao baixar imagem:", e)

    if not imagens:
        return None

    imagens_pil = [Image.open(f).convert("RGB") for f in sorted(imagens)]
    nome_pdf = f"capitulo {numero_capitulo}.pdf"
    caminho_pdf = os.path.join(pasta_manga, nome_pdf)
    imagens_pil[0].save(caminho_pdf, save_all=True, append_images=imagens_pil[1:])

    # Gera thumbnail automaticamente
    gerar_thumbnail(caminho_pdf, nome_pdf, pasta_manga)

    for f in imagens:
        os.remove(f)
    os.rmdir(pasta_temp)
    return caminho_pdf

if __name__ == "__main__":
    app.run(debug=True)