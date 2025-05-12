
import os
import re
import json
import requests
import fitz
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urljoin, urlparse
from flask import Flask, request, redirect, url_for, render_template, flash, send_file

app = Flask(__name__)
app.secret_key = "segredo"
BASE_COMICS = os.path.expanduser("~/Comics")
THUMBNAILS = os.path.join("static", "thumbnails")
URLS_JSON = "urls_salvas.json"

os.makedirs(BASE_COMICS, exist_ok=True)
os.makedirs(THUMBNAILS, exist_ok=True)

def carregar_urls():
    if os.path.exists(URLS_JSON):
        with open(URLS_JSON, "r") as f:
            return json.load(f)
    return {}

def salvar_urls(urls):
    with open(URLS_JSON, "w") as f:
        json.dump(urls, f)

@app.route("/", methods=["GET", "POST"])
def index():
    urls_salvas = carregar_urls()
    base_url = ""

    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "salvar_url":
            nova_url = request.form.get("nova_url").strip()
            nome_manga = request.form.get("nome_manga").strip()
            if nova_url and nome_manga:
                urls_salvas[nome_manga] = nova_url
                salvar_urls(urls_salvas)
                flash(f"URL para '{nome_manga}' salva com sucesso!", "success")

        elif acao == "baixar_manual" or acao == "baixar_predefinida":
            base_url = request.form.get("base_url").strip()
            capitulo = request.form.get("capitulo").strip()

            if not base_url.endswith("-") and not base_url.endswith("/"):
                base_url += "-"

            if not base_url.startswith("http") or not capitulo.isdigit():
                flash("Dados inválidos. Verifique a URL e o número do capítulo.", "error")
                return render_template("index.html", urls_salvas=urls_salvas)

            full_url = f"{base_url}{capitulo}/"
            nome_manga = extrair_nome_manga(base_url)
            resultado = baixar_capitulo_para_pdf(full_url, nome_manga, capitulo)

            if resultado:
                flash(f"PDF salvo em: {resultado}", "success")
            else:
                flash("Nenhuma imagem encontrada ou erro ao baixar.", "error")

        return render_template("index.html", base_url=base_url, urls_salvas=urls_salvas)

    return render_template("index.html", base_url=base_url, urls_salvas=urls_salvas)

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

def extrair_nome_manga(base_url):
    partes = urlparse(base_url).path.strip("/").split("/")
    for i in partes[::-1]:
        if i and "capitulo" not in i:
            return i.replace("-", " ").title()
    return "Manga Desconhecido"

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

    gerar_thumbnail(caminho_pdf, nome_pdf, pasta_manga)

    for f in imagens:
        os.remove(f)
    os.rmdir(pasta_temp)
    return caminho_pdf

if __name__ == "__main__":
    app.run(debug=True)