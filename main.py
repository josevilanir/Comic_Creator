import os
import re
import json
import requests
import fitz
from bs4 import BeautifulSoup
from PIL import Image, UnidentifiedImageError 
from urllib.parse import urljoin, urlparse
from flask import Flask, request, redirect, url_for, render_template, flash, send_file, jsonify
import shutil
import logging # Adicionado na correção anterior


app = Flask(__name__)
app.secret_key = "segredo"
BASE_COMICS = os.path.expanduser("~/Comics")
THUMBNAILS = os.path.join("static", "thumbnails")
URLS_JSON = "urls_salvas.json"

os.makedirs(BASE_COMICS, exist_ok=True)
if not os.path.exists(THUMBNAILS):
    os.makedirs(THUMBNAILS, exist_ok=True)

def carregar_urls():
    if os.path.exists(URLS_JSON):
        with open(URLS_JSON, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                app.logger.error(f"Erro ao decodificar {URLS_JSON}. Retornando dicionário vazio.")
                return {}
    return {}

def salvar_urls(urls):
    with open(URLS_JSON, "w") as f:
        json.dump(urls, f, indent=4)

# NOVA FUNÇÃO AUXILIAR para limpar o sufixo "manga-pt-br" e variações
def limpar_sufixo_manga_pt_br(nome_manga_str):
    if not nome_manga_str or nome_manga_str == "Manga Desconhecido":
        return nome_manga_str

    # Padrões para remover, case insensitive, do final da string
    # Cobre variações como " Manga Pt Br", "-manga-pt-br", "_manga_pt_br"
    # Também cobre casos onde apenas " Pt Br" ou similar está no final.
    patterns_to_remove = [
        r"[ _\-]manga[ _\-]pt[ _\-]br$",
        r"[ _\-]pt[ _\-]br$",
    ]
    
    cleaned_name = nome_manga_str
    for pattern in patterns_to_remove:
        # re.sub substitui o padrão por uma string vazia se encontrado no final
        new_name, num_subs = re.subn(pattern, "", cleaned_name, flags=re.IGNORECASE)
        if num_subs > 0:
            cleaned_name = new_name.strip() # Remove espaços após a substituição
            # Se um padrão mais específico (com "manga") foi removido, podemos parar
            if "manga" in pattern.lower():
                break 
            
    return cleaned_name.strip() if cleaned_name else nome_manga_str # Retorna nome limpo ou original se limpeza resultar em vazio


def extrair_nome_manga(base_url):
    partes = urlparse(base_url).path.strip("/").split("/")
    for i in partes[::-1]:
        if i and "capitulo" not in i.lower() and "chap" not in i.lower():
            nome_bruto = i.replace("-", " ").title()
            # A limpeza do sufixo "Manga Pt Br" será feita na rota index após obter este nome bruto
            return nome_bruto 
    return "Manga Desconhecido"

@app.route("/", methods=["GET", "POST"])
def index():
    urls_salvas = carregar_urls()
    base_url_for_template = request.args.get("base_url", "")

    if request.method == "POST":
        acao = request.form.get("acao")
        base_url_for_template = request.form.get("base_url", base_url_for_template)

        if acao == "salvar_url":
            nova_url = request.form.get("nova_url", "").strip()
            nome_manga_key = request.form.get("nome_manga", "").strip()
            if nova_url and nome_manga_key:
                urls_salvas[nome_manga_key] = nova_url
                salvar_urls(urls_salvas)
                flash(f"URL para '{nome_manga_key}' salva com sucesso!", "success")
            else:
                flash("Nome do mangá e URL são obrigatórios para salvar.", "error")
            return redirect(url_for("index", base_url=nova_url if (nova_url and nome_manga_key) else base_url_for_template))

        elif acao == "remover_url":
            nome_manga_key = request.form.get("nome_manga", "").strip()
            if nome_manga_key in urls_salvas:
                urls_salvas.pop(nome_manga_key)
                salvar_urls(urls_salvas)
                flash(f"URL de '{nome_manga_key}' removida com sucesso!", "success")
            else:
                flash(f"URL para '{nome_manga_key}' não encontrada.", "error")
            return redirect(url_for("index", base_url=base_url_for_template))

        elif acao == "baixar_manual" or acao == "baixar_predefinida":
            base_url_from_form = request.form.get("base_url", "").strip()
            capitulo_str = request.form.get("capitulo", "").strip()
            nome_manga_key_from_form = request.form.get("nome_manga", "").strip()
            base_url_for_template = base_url_from_form

            if not (base_url_from_form and capitulo_str and capitulo_str.isdigit()):
                flash("Dados inválidos. Verifique a URL base e o número do capítulo.", "error")
                return render_template("index.html", urls_salvas=urls_salvas, base_url=base_url_for_template)

            url_construction_suffix = ""
            string_to_check_for_ptbr = nome_manga_key_from_form + " " + base_url_from_form if acao == "baixar_predefinida" and nome_manga_key_from_form else base_url_from_form
            
            if "manga-pt-br" in string_to_check_for_ptbr.lower():
                url_construction_suffix = "-pt-br"
            
            final_chapter_page_url = f"{base_url_from_form}{capitulo_str}{url_construction_suffix}/"
            
            url_for_folder_name_extraction = base_url_from_form
            if url_for_folder_name_extraction.lower().endswith("capitulo-"):
                url_for_folder_name_extraction = url_for_folder_name_extraction[:-len("capitulo-")]
            elif url_for_folder_name_extraction.lower().endswith("chap-"):
                url_for_folder_name_extraction = url_for_folder_name_extraction[:-len("chap-")]
            
            nome_manga_para_pasta_bruto = extrair_nome_manga(url_for_folder_name_extraction)

            if acao == "baixar_predefinida" and nome_manga_key_from_form:
                # Para predefinidas, a chave é a fonte primária do nome, mesmo que extrair_nome_manga dê algo
                nome_manga_para_pasta = nome_manga_key_from_form
            else:
                nome_manga_para_pasta = nome_manga_para_pasta_bruto
            
            # Limpar o sufixo "-manga-pt-br" e variações do nome final da pasta
            if nome_manga_para_pasta and nome_manga_para_pasta != "Manga Desconhecido":
                nome_manga_para_pasta_limpo = limpar_sufixo_manga_pt_br(nome_manga_para_pasta)
                # Se a limpeza resultar em string vazia, reverte para o nome bruto (ou chave) não limpo
                # ou para "Manga Desconhecido" se o nome bruto também for problemático.
                if not nome_manga_para_pasta_limpo and nome_manga_para_pasta_bruto and nome_manga_para_pasta_bruto != "Manga Desconhecido":
                    nome_manga_para_pasta = nome_manga_para_pasta_bruto # Usa o bruto não limpo
                elif nome_manga_para_pasta_limpo:
                    nome_manga_para_pasta = nome_manga_para_pasta_limpo
                elif not nome_manga_para_pasta_limpo and (not nome_manga_para_pasta_bruto or nome_manga_para_pasta_bruto == "Manga Desconhecido"):
                     nome_manga_para_pasta = "Manga_Sem_Nome_Definido" # Fallback final


            app.logger.info(f"Tentando baixar: Manga '{nome_manga_para_pasta}', Capitulo '{capitulo_str}'. URL: '{final_chapter_page_url}'")
            resultado_download = baixar_capitulo_para_pdf(final_chapter_page_url, nome_manga_para_pasta, capitulo_str)

            if resultado_download:
                flash(f"Download do capítulo {capitulo_str} de '{nome_manga_para_pasta}' concluído! PDF: {resultado_download}", "success")
            
            return redirect(url_for("index", base_url=base_url_from_form))

        return render_template("index.html", urls_salvas=urls_salvas, base_url=base_url_for_template)

    return render_template("index.html", urls_salvas=urls_salvas, base_url=base_url_for_template)

# --- Sua função baixar_capitulo_para_pdf (versão robusta mais recente) ---
# (Cole aqui a versão completa e mais recente da sua função baixar_capitulo_para_pdf)
def baixar_capitulo_para_pdf(url, nome_manga, numero_capitulo):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        app.logger.info(f"Acessando URL do capítulo: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Erro ao acessar a URL do capítulo {url}: {e}")
        flash(f"Erro ao acessar a URL do capítulo. Verifique o link. Detalhe: {e}", "error")
        return None
    except Exception as e: 
        app.logger.error(f"Erro ao processar HTML da URL {url}: {e}")
        flash(f"Erro ao processar o conteúdo da página do capítulo. Detalhe: {e}", "error")
        return None

    tags = soup.find_all("img")
    imagens_baixadas_paths = []
    
    # Limpeza e formatação do nome_manga para nome de pasta seguro
    nome_manga_seguro = re.sub(r'[^\w\s-]', '', nome_manga).strip().replace(" ", "_")
    if not nome_manga_seguro:
        nome_manga_seguro = "Manga_Desconhecido_Pasta" # Nome de pasta fallback
        
    pasta_manga_destino = os.path.join(BASE_COMICS, nome_manga_seguro)
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
        
        parsed_path = urlparse(full_img_url).path.lower()
        if any(parsed_path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']) or not os.path.splitext(parsed_path)[1]:
            return full_img_url
        return None

    app.logger.info(f"Encontradas {len(tags)} tags <img>. Filtrando e baixando imagens para {nome_manga_seguro} Cap. {numero_capitulo}...")
    img_save_counter = 0

    for tag in tags:
        img_url = get_img_url_from_tag(tag, url)
        
        if img_url:
            try:
                img_filename = os.path.basename(urlparse(img_url).path)
                name_part, ext_part = os.path.splitext(img_filename)
                ext_part = ext_part.lower()

                is_potential_page = False
                if name_part.isdigit() and (1 <= len(name_part) <= 3):
                    is_potential_page = True
                    app.logger.debug(f"Imagem '{img_filename}' corresponde ao padrão numérico direto.")
                
                if not is_potential_page:
                    if re.search(r'(page|p|img|scan|pagina|capitulo|chapter|ch)[\W_]*(\d+)|(\b\d{1,3}\b)', name_part, re.IGNORECASE):
                        is_potential_page = True
                        app.logger.debug(f"Imagem '{img_filename}' corresponde ao padrão de nomeação de página.")
                
                if not is_potential_page:
                    app.logger.debug(f"Imagem '{img_filename}' de {img_url} não parece ser uma página de capítulo. Pulando.")
                    continue
                
                app.logger.info(f"Tentando baixar imagem candidata: {img_url}")
                img_response = requests.get(img_url, headers=headers, timeout=20, stream=True)
                img_response.raise_for_status()

                content_type = img_response.headers.get('Content-Type', '').lower()
                if not content_type.startswith('image/'):
                    app.logger.warning(f"Conteúdo não é imagem (Content-Type: {content_type}) para {img_url}. Pulando.")
                    continue

                img_data = img_response.content
                if not img_data:
                    app.logger.warning(f"Imagem vazia de {img_url}. Pulando.")
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
                app.logger.debug(f"Imagem baixada e salva: {caminho_img_salva}")
                img_save_counter += 1

            except requests.exceptions.RequestException as e_req:
                app.logger.warning(f"Erro de request ao baixar/verificar imagem {img_url}: {e_req}")
            except Exception as e_gen:
                app.logger.warning(f"Erro geral ao processar imagem candidata {img_url}: {e_gen}")

    if not imagens_baixadas_paths:
        app.logger.warning(f"Nenhuma imagem de capítulo foi baixada de {url}.")
        flash("Nenhuma imagem de capítulo foi encontrada ou baixada (verifique os logs para detalhes).", "error")
        if os.path.exists(pasta_temp): shutil.rmtree(pasta_temp)
        return None

    app.logger.info(f"Processando {len(imagens_baixadas_paths)} imagens baixadas com PIL...")
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
            app.logger.debug(f"Imagem processada com PIL: {f_path}")
        except UnidentifiedImageError:
            app.logger.warning(f"PIL.UnidentifiedImageError: Não foi possível identificar: {f_path}. Pulando.")
        except Exception as e:
            app.logger.error(f"Erro ao abrir/converter imagem {f_path} com PIL: {e}. Pulando.")

    if not imagens_pil:
        app.logger.error(f"Nenhuma imagem pôde ser processada com PIL para o capítulo {url}.")
        flash("Nenhuma imagem pôde ser processada para criar o PDF.", "error")
        if os.path.exists(pasta_temp): shutil.rmtree(pasta_temp)
        return None
    
    nome_pdf_arquivo = f"capitulo_{str(numero_capitulo).zfill(3)}.pdf"
    caminho_pdf_final = os.path.join(pasta_manga_destino, nome_pdf_arquivo)
    
    try:
        app.logger.info(f"Salvando PDF em: {caminho_pdf_final}")
        imagens_pil[0].save(
            caminho_pdf_final, 
            save_all=True, 
            append_images=imagens_pil[1:],
            resolution=100.0 
        )
    except Exception as e:
        app.logger.error(f"Erro ao salvar o PDF {caminho_pdf_final}: {e}")
        flash(f"Erro ao criar o arquivo PDF final: {e}", "error")
        if os.path.exists(pasta_temp): shutil.rmtree(pasta_temp)
        return None

    gerar_thumbnail(caminho_pdf_final, nome_pdf_arquivo, pasta_manga_destino)

    app.logger.info(f"Limpando pasta temporária: {pasta_temp}")
    if os.path.exists(pasta_temp): shutil.rmtree(pasta_temp)
        
    return caminho_pdf_final


# --- Suas outras rotas e funções auxiliares (biblioteca, listar_pasta, etc.) ---
# (Cole aqui o restante das suas funções: biblioteca, listar_pasta, visualizar_pdf, upload_capa, excluir_capitulo, excluir_manga, gerar_thumbnail)
@app.route("/biblioteca")
def biblioteca():
    pastas = []
    for item in os.listdir(BASE_COMICS):
        caminho_completo_item = os.path.join(BASE_COMICS, item)
        if os.path.isdir(caminho_completo_item):
            capa_path = os.path.join(caminho_completo_item, "capa.jpg")
            tem_capa = os.path.exists(capa_path)
            pastas.append({
                "nome": item,
                "tem_capa": tem_capa,
                "capa_url": url_for('visualizar_pdf', manga=item, arquivo="capa.jpg") if tem_capa else None
            })
    pastas = sorted(pastas, key=lambda p: p['nome'].lower())
    return render_template("biblioteca.html", pastas=pastas)

@app.route("/pasta/<path:nome_pasta>")
def listar_pasta(nome_pasta):
    pasta = os.path.join(BASE_COMICS, nome_pasta)
    if not os.path.isdir(pasta):
        flash(f"Pasta '{nome_pasta}' não encontrada.", "error")
        return redirect(url_for("biblioteca"))

    ordem = request.args.get("ordem", "asc")

    try:
        arquivos = sorted(
            [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")],
            key=lambda nome: int("".join(filter(str.isdigit, os.path.splitext(nome)[0])) or 0),
            reverse=(ordem == "desc")
        )
    except ValueError:
        app.logger.warning(f"Falha na ordenação numérica para {nome_pasta}, usando alfabética.")
        arquivos = sorted(
            [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")],
            reverse=(ordem == "desc")
        )
        
    return render_template("lista_pdfs.html", nome_pasta=nome_pasta, arquivos=arquivos, ordem=ordem)


@app.route("/visualizar/<path:manga>/<path:arquivo>")
def visualizar_pdf(manga, arquivo):
    manga_seguro = os.path.normpath(manga)
    arquivo_seguro = os.path.normpath(arquivo)

    if manga_seguro.startswith("..") or arquivo_seguro.startswith("..") or \
       "/" in manga_seguro or "\\" in manga_seguro:
        app.logger.warning(f"Tentativa de acesso a caminho inválido: manga='{manga}', arquivo='{arquivo}'")
        return "Acesso negado a caminho inválido.", 403

    caminho_completo = os.path.abspath(os.path.join(BASE_COMICS, manga_seguro, arquivo_seguro))
    base_comics_abs = os.path.abspath(BASE_COMICS)

    if not caminho_completo.startswith(base_comics_abs):
        app.logger.warning(f"Tentativa de acesso fora do diretório base: '{caminho_completo}'")
        return "Acesso negado.", 403

    if os.path.exists(caminho_completo) and os.path.isfile(caminho_completo):
        return send_file(caminho_completo)
    
    app.logger.error(f"Arquivo não encontrado em visualizar_pdf: {caminho_completo}")
    return "Arquivo não encontrado", 404

@app.route("/upload_capa/<path:nome_pasta>", methods=["POST"])
def upload_capa(nome_pasta):
    nome_pasta_seguro = os.path.normpath(nome_pasta)
    if nome_pasta_seguro.startswith("..") or "/" in nome_pasta_seguro or "\\" in nome_pasta_seguro:
        flash("Nome de pasta inválido.", "error")
        return redirect(url_for("biblioteca"))

    pasta_destino = os.path.abspath(os.path.join(BASE_COMICS, nome_pasta_seguro))
    base_comics_abs = os.path.abspath(BASE_COMICS)

    if not pasta_destino.startswith(base_comics_abs):
        flash("Acesso negado à pasta.", "error")
        return redirect(url_for("biblioteca"))

    if not os.path.exists(pasta_destino) or not os.path.isdir(pasta_destino):
        flash("Pasta do mangá não encontrada.", "error")
        return redirect(url_for("biblioteca"))

    if "capa" not in request.files:
        flash("Nenhum arquivo de capa enviado.", "error")
        return redirect(url_for("biblioteca"))

    file = request.files["capa"]
    if file.filename == "":
        flash("Arquivo de capa sem nome.", "error")
        return redirect(url_for("biblioteca"))

    extensoes_permitidas = {'png', 'jpg', 'jpeg', 'webp'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in extensoes_permitidas:
        flash("Formato de arquivo de capa inválido. Use PNG, JPG, JPEG ou WEBP.", "error")
        return redirect(url_for("biblioteca"))

    try:
        caminho_capa_final = os.path.join(pasta_destino, "capa.jpg")
        Image.open(file.stream).convert("RGB").save(caminho_capa_final, "JPEG")
        flash(f"Capa atualizada para {nome_pasta_seguro}.", "success")
    except Exception as e:
        app.logger.error(f"Erro ao salvar capa para {nome_pasta_seguro}: {e}")
        flash("Erro ao processar ou salvar a imagem da capa.", "error")
        
    return redirect(url_for("biblioteca"))


@app.route("/excluir_capitulo/<path:manga>/<path:arquivo>", methods=["DELETE"])
def excluir_capitulo(manga, arquivo):
    manga_seguro = os.path.normpath(manga)
    arquivo_seguro = os.path.normpath(arquivo)

    if manga_seguro.startswith("..") or "/" in manga_seguro or "\\" in manga_seguro or \
       arquivo_seguro.startswith("..") or "/" in arquivo_seguro or "\\" in arquivo_seguro:
        return jsonify({"success": False, "message": "Nome de mangá ou arquivo inválido."}), 400
    
    caminho_pasta_manga_base = os.path.abspath(BASE_COMICS)
    caminho_pdf_completo = os.path.abspath(os.path.join(BASE_COMICS, manga_seguro, arquivo_seguro))
    
    nome_base_arquivo, _ = os.path.splitext(arquivo_seguro)
    caminho_thumb_completo = os.path.abspath(os.path.join(BASE_COMICS, manga_seguro, nome_base_arquivo + ".jpg"))

    if not caminho_pdf_completo.startswith(caminho_pasta_manga_base) or \
       (os.path.exists(caminho_thumb_completo) and not caminho_thumb_completo.startswith(caminho_pasta_manga_base)): # Verifica thumb apenas se existir
        app.logger.warning(f"Tentativa de acesso inválido para exclusão: Manga '{manga_seguro}', Arquivo '{arquivo_seguro}'")
        return jsonify({"success": False, "message": "Acesso negado."}), 403

    try:
        pdf_excluido = False
        if os.path.exists(caminho_pdf_completo) and os.path.isfile(caminho_pdf_completo):
            os.remove(caminho_pdf_completo)
            pdf_excluido = True
            app.logger.info(f"Capítulo PDF excluído: {caminho_pdf_completo}")
        else:
            app.logger.warning(f"Capítulo PDF não encontrado para exclusão: {caminho_pdf_completo}")

        if os.path.exists(caminho_thumb_completo) and os.path.isfile(caminho_thumb_completo):
            os.remove(caminho_thumb_completo)
            app.logger.info(f"Thumbnail do capítulo excluído: {caminho_thumb_completo}")
        
        if pdf_excluido:
            return jsonify({"success": True, "message": f"Capítulo '{arquivo_seguro.replace('.pdf', '')}' excluído com sucesso!"})
        else:
            return jsonify({"success": False, "message": "Arquivo do capítulo não encontrado."}), 404

    except Exception as e:
        app.logger.error(f"Erro ao excluir capítulo '{arquivo_seguro}' de '{manga_seguro}': {e}")
        return jsonify({"success": False, "message": f"Erro interno ao excluir o capítulo: {str(e)}"}), 500


@app.route("/excluir_manga/<path:nome_manga>", methods=["DELETE"])
def excluir_manga(nome_manga):
    manga_seguro = os.path.normpath(nome_manga)
    if manga_seguro.startswith("..") or "/" in manga_seguro or "\\" in manga_seguro :
        return jsonify({"success": False, "message": "Nome de mangá inválido."}), 400

    caminho_pasta_manga_base = os.path.abspath(BASE_COMICS)
    caminho_pasta_manga_completo = os.path.abspath(os.path.join(BASE_COMICS, manga_seguro))

    if not caminho_pasta_manga_completo.startswith(caminho_pasta_manga_base) or caminho_pasta_manga_completo == caminho_pasta_manga_base:
        app.logger.warning(f"Tentativa de acesso inválido para exclusão de mangá: '{manga_seguro}'")
        return jsonify({"success": False, "message": "Acesso negado."}), 403
    
    try:
        if os.path.exists(caminho_pasta_manga_completo) and os.path.isdir(caminho_pasta_manga_completo):
            shutil.rmtree(caminho_pasta_manga_completo)
            app.logger.info(f"Mangá excluído: {caminho_pasta_manga_completo}")
            
            urls_salvas = carregar_urls()
            # Limpa o nome da pasta da mesma forma que faríamos para criar, para garantir que a chave corresponda
            chave_manga_limpa = limpar_sufixo_manga_pt_br(manga_seguro.replace("_", " ").title()) # Simula como a chave poderia ser se não fosse idêntica ao nome da pasta
            chave_manga_original = manga_seguro # O nome da pasta, que pode ser "Nome_Manga" ou "Nome_Manga_Pt_Br"

            # Tenta remover a chave que corresponde exatamente ao nome da pasta
            # E também uma versão "limpa" da chave, caso o usuário tenha salvo a URL predefinida com o nome já limpo
            chaves_para_tentar_remover = {chave_manga_original, chave_manga_limpa}
            
            for chave in chaves_para_tentar_remover:
                if chave in urls_salvas:
                    del urls_salvas[chave]
                    salvar_urls(urls_salvas)
                    app.logger.info(f"URL predefinida para '{chave}' removida.")
                    # Se removeu uma, pode parar ou continuar se houver chance de duplicatas com nomes ligeiramente diferentes
                    # Para este caso, assumimos que uma remoção é suficiente.

            return jsonify({"success": True, "message": f"Mangá '{manga_seguro}' e todos os seus capítulos foram excluídos."})
        else:
            app.logger.warning(f"Pasta do mangá não encontrada para exclusão: {caminho_pasta_manga_completo}")
            return jsonify({"success": False, "message": "Pasta do mangá não encontrada."}), 404
    except Exception as e:
        app.logger.error(f"Erro ao excluir o mangá '{manga_seguro}': {e}")
        return jsonify({"success": False, "message": f"Erro interno ao excluir o mangá: {str(e)}"}), 500


def gerar_thumbnail(caminho_pdf, nome_pdf, pasta_manga):
    try:
        doc = fitz.open(caminho_pdf)
        if doc.page_count > 0:
            page = doc.load_page(0) 
            pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
            thumb_name = nome_pdf.replace(".pdf", ".jpg")
            caminho_thumb = os.path.join(pasta_manga, thumb_name)
            
            pix.save(caminho_thumb)
            app.logger.info(f"✓ Thumbnail salva: {caminho_thumb}")
        else:
            app.logger.warning(f"PDF '{nome_pdf}' não tem páginas para gerar thumbnail.")
    except Exception as e:
        app.logger.error(f"Erro ao gerar thumbnail para {nome_pdf}: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) # Alterado para INFO para produção, DEBUG para desenvolvimento
    app.run(debug=True)