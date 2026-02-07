# app/downloader.py
import os
import re
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse, urljoin


def baixar_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def limpar_sufixo(nome):
    return re.sub(r'[-_\s]*(capit[úu]lo|chapter)?\s*\d+.*$', '', nome, flags=re.IGNORECASE).strip()


def extrair_nome_manga(url):
    nome = os.path.basename(urlparse(url).path)
    nome = limpar_sufixo(nome)
    return nome or "manga_desconhecido"


def get_img_url_from_tag(tag, url_base):
    img_url = tag.get("src") or tag.get("data-src") or tag.get("data-lazy-src")
    if not img_url:
        return None

    img_url = urljoin(url_base, img_url)
    nome_arquivo = os.path.basename(urlparse(img_url).path)
    nome_sem_ext = os.path.splitext(nome_arquivo)[0].lower()

    if re.search(r'(^\d+[_-]?image)|(^\d+$)|((page|p|img|scan|pagina|capitulo|chapter|ch)[\W_]*\d+)', nome_sem_ext, re.IGNORECASE):
        return img_url
    return None


def filtrar_urls_imagens(html, url_base):
    soup = BeautifulSoup(html, "html.parser")
    tags_imagem = soup.find_all("img")
    urls = []

    for tag in tags_imagem:
        url_img = get_img_url_from_tag(tag, url_base)
        if url_img:
            urls.append(url_img)

    return sorted(set(urls))


def baixar_imagem(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    except Exception:
        return None


def salvar_pdf_com_imagens(imagens, caminho_pdf):
    if not imagens:
        return False

    try:
        imagens[0].save(caminho_pdf, save_all=True, append_images=imagens[1:])
        return True
    except Exception:
        return False


def baixar_capitulo_para_pdf(url_capitulo, caminho_saida):
    html = baixar_html(url_capitulo)
    if not html:
        return False, "Falha ao baixar a página HTML."

    imagens_urls = filtrar_urls_imagens(html, url_capitulo)
    if not imagens_urls:
        return False, "Nenhuma imagem válida encontrada."

    imagens = [img for url in imagens_urls if (img := baixar_imagem(url)) is not None]

    if not imagens:
        return False, "Não foi possível baixar nenhuma imagem."

    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    if salvar_pdf_com_imagens(imagens, caminho_saida):
        return True, f"Capítulo salvo em {caminho_saida}"
    else:
        return False, "Erro ao salvar o PDF."
