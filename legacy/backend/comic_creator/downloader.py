import os
import re
import shutil
import requests
import fitz
from bs4 import BeautifulSoup
from PIL import Image, UnidentifiedImageError
from urllib.parse import urljoin, urlparse
from flask import current_app, flash


# Parte principal de download de capítulos

def baixar_capitulo_para_pdf(url, nome_manga, numero_capitulo):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        current_app.logger.info(f"Acessando URL do capítulo: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao acessar a URL do capítulo {url}: {e}")
        flash(f"Erro ao acessar a URL do capítulo. Verifique o link. Detalhe: {e}", "error")
        return None
    except Exception as e:
        current_app.logger.error(f"Erro ao processar HTML da URL {url}: {e}")
        flash(f"Erro ao processar o conteúdo da página do capítulo. Detalhe: {e}", "error")
        return None

    tags = soup.find_all("img")
    imagens_baixadas_paths = []

    nome_manga_seguro = re.sub(r'[^\w\s-]', '', nome_manga).strip().replace(" ", "_")
    if not nome_manga_seguro:
        nome_manga_seguro = "Manga_Desconhecido_Pasta"

    base_dir = current_app.config['BASE_COMICS']
    pasta_manga_destino = os.path.join(base_dir, nome_manga_seguro)
    pasta_temp = os.path.join(pasta_manga_destino, "tmp")
    os.makedirs(pasta_temp, exist_ok=True)

    def get_img_url_from_tag(tag_element, base_chapter_url):
        attributes_to_check = ["data-src", "src", "data-lazy-src", "data-original", "data-lazyload"]
        img_src_url = None
        for attr in attributes_to_check:
            src_candidate = tag_element.get(attr)
            if src_candidate and isinstance(src_candidate, str):
                src_candidate = src_candidate.strip()
                if src_candidate and not src_candidate.startswith("data:image"):
                    img_src_url = src_candidate
                    break
        if not img_src_url:
            return None

        full_img_url = urljoin(base_chapter_url, img_src_url)
        parsed_path = full_img_url.lower()

        if 'wp-content/uploads/wp-manga/data/manga_' in parsed_path and '_image.jpeg' in parsed_path:
            return full_img_url
        if 'wp-manga' in parsed_path and ('/data/' in parsed_path or '/content/' in parsed_path):
            return full_img_url
        filename = os.path.basename(urlparse(full_img_url).path)
        name_part = os.path.splitext(filename)[0].lower()
        if name_part.isdigit() and (1 <= len(name_part) <= 4):
            return full_img_url
        if re.search(r'(^\d+[_-]image$)|(^\d+$)|((page|p|img|scan|pagina|capitulo|chapter|ch)[\W_]*\d+)', name_part, re.IGNORECASE):
            return full_img_url
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        if not any(filename.lower().endswith(ext) for ext in valid_extensions):
            return None
        return None

    current_app.logger.info(f"Encontradas {len(tags)} tags <img>. Filtrando e baixando imagens para {nome_manga_seguro} Cap. {numero_capitulo}...")
    img_save_counter = 0

    for tag in tags:
        img_url = get_img_url_from_tag(tag, url)
        if img_url:
            current_app.logger.debug(f"Imagem candidata encontrada: {img_url}")
            try:
                if '/wp-manga/data/manga_' in img_url.lower():
                    page_match = re.search(r'/(\d+)_image\.jpeg', img_url, re.IGNORECASE)
                    if page_match:
                        img_save_counter = int(page_match.group(1)) - 1
                img_filename = os.path.basename(urlparse(img_url).path)
                name_part, ext_part = os.path.splitext(img_filename)
                ext_part = ext_part.lower()
                is_potential_page = False
                if name_part.isdigit() and (1 <= len(name_part) <= 3):
                    is_potential_page = True
                if not is_potential_page:
                    if re.search(r'(^\d+[_-]image$)|(^\d+$)|((page|p|img|scan|pagina|capitulo|chapter|ch)[\W_]*\d+)', name_part, re.IGNORECASE):
                        is_potential_page = True
                if not is_potential_page:
                    current_app.logger.debug(f"Imagem '{img_filename}' de {img_url} n\u00e3o parece ser uma p\u00e1gina de cap\u00edtulo. Pulando.")
                    continue
                current_app.logger.info(f"Tentando baixar imagem candidata: {img_url}")
                img_response = requests.get(img_url, headers=headers, timeout=20, stream=True)
                img_response.raise_for_status()

                content_type = img_response.headers.get('Content-Type', '').lower()
                if not content_type.startswith('image/'):
                    current_app.logger.warning(f"Conte\u00fado n\u00e3o é imagem (Content-Type: {content_type}) para {img_url}. Pulando.")
                    continue
                img_data = img_response.content
                if not img_data:
                    current_app.logger.warning(f"Imagem vazia de {img_url}. Pulando.")
                    continue
                final_extension = '.jpg'
                if content_type.startswith('image/jpeg'): final_extension = '.jpg'
                elif content_type.startswith('image/png'): final_extension = '.png'
                elif content_type.startswith('image/webp'): final_extension = '.webp'
                elif content_type.startswith('image/gif'): final_extension = '.gif'
                elif ext_part in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                    final_extension = ext_part
                nome_img_salva_temp = f"{str(img_save_counter).zfill(3)}{final_extension}"
                caminho_img_salva = os.path.join(pasta_temp, nome_img_salva_temp)
                with open(caminho_img_salva, "wb") as f:
                    f.write(img_data)
                imagens_baixadas_paths.append(caminho_img_salva)
                current_app.logger.debug(f"Imagem baixada e salva: {caminho_img_salva}")
                img_save_counter += 1
            except requests.exceptions.RequestException as e_req:
                current_app.logger.warning(f"Erro de request ao baixar/verificar imagem {img_url}: {e_req}")
            except Exception as e_gen:
                current_app.logger.warning(f"Erro geral ao processar imagem candidata {img_url}: {e_gen}")
        else:
            current_app.logger.debug(f"Imagem ignorada - Tag: {tag}")

    if not imagens_baixadas_paths:
        current_app.logger.warning(f"Nenhuma imagem de capítulo foi baixada de {url}.")
        flash("Nenhuma imagem de capítulo foi encontrada ou baixada (verifique os logs para detalhes).", "error")
        if os.path.exists(pasta_temp):
            shutil.rmtree(pasta_temp)
        return None

    current_app.logger.info(f"Processando {len(imagens_baixadas_paths)} imagens baixadas com PIL...")
    imagens_pil = []
    for f_path in sorted(imagens_baixadas_paths):
        try:
            img = Image.open(f_path)
            if img.mode == 'P' and 'transparency' in img.info:
                img = img.convert('RGBA')
            if img.mode == 'RGBA':
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                imagens_pil.append(background)
            else:
                imagens_pil.append(img.convert("RGB"))
            current_app.logger.debug(f"Imagem processada com PIL: {f_path}")
        except UnidentifiedImageError:
            current_app.logger.warning(f"PIL.UnidentifiedImageError: N\u00e3o foi poss\u00edvel identificar: {f_path}. Pulando.")
        except Exception as e:
            current_app.logger.error(f"Erro ao abrir/converter imagem {f_path} com PIL: {e}. Pulando.")

    if not imagens_pil:
        current_app.logger.error(f"Nenhuma imagem p\u00f4de ser processada com PIL para o cap\u00edtulo {url}.")
        flash("Nenhuma imagem p\u00f4de ser processada para criar o PDF.", "error")
        if os.path.exists(pasta_temp):
            shutil.rmtree(pasta_temp)
        return None

    nome_pdf_arquivo = f"capitulo_{str(numero_capitulo).zfill(3)}.pdf"
    caminho_pdf_final = os.path.join(pasta_manga_destino, nome_pdf_arquivo)
    try:
        current_app.logger.info(f"Salvando PDF em: {caminho_pdf_final}")
        imagens_pil[0].save(
            caminho_pdf_final,
            save_all=True,
            append_images=imagens_pil[1:],
            resolution=100.0
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar o PDF {caminho_pdf_final}: {e}")
        flash(f"Erro ao criar o arquivo PDF final: {e}", "error")
        if os.path.exists(pasta_temp):
            shutil.rmtree(pasta_temp)
        return None

    gerar_thumbnail(caminho_pdf_final, nome_pdf_arquivo, pasta_manga_destino)

    current_app.logger.info(f"Limpando pasta tempor\u00e1ria: {pasta_temp}")
    if os.path.exists(pasta_temp):
        shutil.rmtree(pasta_temp)

    return caminho_pdf_final


def gerar_thumbnail(caminho_pdf, nome_pdf, pasta_manga):
    try:
        doc = fitz.open(caminho_pdf)
        if doc.page_count > 0:
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
            thumb_name = nome_pdf.replace('.pdf', '.jpg')
            caminho_thumb = os.path.join(pasta_manga, thumb_name)
            pix.save(caminho_thumb)
            current_app.logger.info(f"\u2713 Thumbnail salva: {caminho_thumb}")
        else:
            current_app.logger.warning(f"PDF '{nome_pdf}' n\u00e3o tem p\u00e1ginas para gerar thumbnail.")
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar thumbnail para {nome_pdf}: {e}")

