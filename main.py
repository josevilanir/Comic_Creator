import os
import re
import json
import requests
import fitz
from bs4 import BeautifulSoup
from PIL import Image, UnidentifiedImageError 
from urllib.parse import urljoin, urlparse
from flask import Flask, request, redirect, url_for, render_template, flash, send_file
import shutil # Importar shutil para exclusão de pastas


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

        elif acao == "remover_url":
            nome_manga = request.form.get("nome_manga").strip()
            if nome_manga in urls_salvas:
                urls_salvas.pop(nome_manga)
                salvar_urls(urls_salvas)
                flash(f"URL de '{nome_manga}' removida com sucesso!", "success")

        elif acao == "baixar_manual" or acao == "baixar_predefinida":
            base_url = request.form.get("base_url").strip()
            capitulo = request.form.get("capitulo").strip()
            
            # Determine the pattern
            padrao = "capitulo"  # default value
            if base_url in [v if isinstance(v, str) else v.get("url") for v in urls_salvas.values()]:
                for nome, dados in urls_salvas.items():
                    if isinstance(dados, dict) and dados.get("url") == base_url:
                        padrao = dados.get("padrao", "capitulo")
                        break
            elif "chap" in base_url:
                padrao = "chap"

            if not base_url.endswith("-") and not base_url.endswith("/"):
                base_url += "-"

            if ("{{" not in base_url and not base_url.startswith("http")) or not capitulo.isdigit():
                flash("Dados inválidos. Verifique a URL e o número do capítulo.", "error")
                return render_template("index.html", urls_salvas=urls_salvas)

            # Build URL based on pattern
            nome_manga = next((k for k, v in urls_salvas.items() if v == base_url), "")
            sufixo = "-pt-br" if nome_manga.lower().endswith("pt-br") else ""
            if padrao == "capitulo":
                full_url = f"{base_url}{capitulo}{sufixo}/"
            elif padrao == "chap":
                full_url = f"{base_url}{capitulo}{sufixo}/"
            else:
                full_url = f"{base_url}{capitulo}{sufixo}/"

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

    ordem = request.args.get("ordem", "asc")

    arquivos = sorted(
        [f for f in os.listdir(pasta) if f.endswith(".pdf")],
        key=lambda nome: int("".join(filter(str.isdigit, nome))),
        reverse=(ordem == "desc")
    )
    return render_template("lista_pdfs.html", nome_pasta=nome_pasta, arquivos=arquivos, ordem=ordem)

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
        if i and "capitulo" not in i and "chap" not in i:
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
    except Exception as e: # Captura outros erros de BeautifulSoup, etc.
        app.logger.error(f"Erro ao processar HTML da URL {url}: {e}")
        flash(f"Erro ao processar o conteúdo da página do capítulo. Detalhe: {e}", "error")
        return None

    tags = soup.find_all("img")
    imagens_baixadas_paths = []
    
    nome_manga_seguro = re.sub(r'[^\w\s-]', '', nome_manga).strip()
    if not nome_manga_seguro:
        nome_manga_seguro = "Manga_Desconhecido" # Evitar nomes vazios
        
    pasta_manga_destino = os.path.join(BASE_COMICS, nome_manga_seguro)
    pasta_temp = os.path.join(pasta_manga_destino, "tmp")
    os.makedirs(pasta_temp, exist_ok=True)

    def get_img_url_from_tag(tag_element, base_chapter_url):
        attributes_to_check = ["data-src", "src", "data-lazy-src", "data-original", "data-lazyload"] # Adicionado data-lazyload
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
        
        # Verificação básica de extensão no URL (ajuda, mas Content-Type é mais confiável)
        parsed_path = urlparse(full_img_url).path.lower()
        if any(parsed_path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']) or not os.path.splitext(parsed_path)[1]: # Ou se não tiver extensão (dinâmico)
            return full_img_url
        return None

    app.logger.info(f"Encontradas {len(tags)} tags <img>. Filtrando e baixando imagens para {nome_manga_seguro} Cap. {numero_capitulo}...")
    img_save_counter = 0 # Contador para nomear arquivos baixados sequencialmente

    for tag in tags:
        img_url = get_img_url_from_tag(tag, url)
        
        if img_url:
            try:
                img_filename = os.path.basename(urlparse(img_url).path)
                name_part, ext_part = os.path.splitext(img_filename)
                ext_part = ext_part.lower()

                is_potential_page = False
                # Critério 1: Nome do arquivo é puramente numérico (ex: "01.jpg", "002.png")
                if name_part.isdigit() and (1 <= len(name_part) <= 3): # 1 a 3 dígitos
                    is_potential_page = True
                    app.logger.debug(f"Imagem '{img_filename}' corresponde ao padrão numérico direto.")
                
                # Critério 2: Nome do arquivo contém padrões comuns de numeração de página
                # (ex: "page_01.jpg", "scan-002.png", "chapter_03_page_001.webp")
                if not is_potential_page:
                    # Procura por "palavra-chave" + número OU número isolado (com cuidado)
                    # \b(\d{1,3})\b : número isolado de 1 a 3 dígitos (como palavra inteira)
                    # (page|p|img|scan|pagina|capitulo|chapter|ch)[\W_]*(\d+) : palavra chave seguida de número
                    if re.search(r'(page|p|img|scan|pagina|capitulo|chapter|ch)[\W_]*(\d+)|(\b\d{1,3}\b)', name_part, re.IGNORECASE):
                        is_potential_page = True
                        app.logger.debug(f"Imagem '{img_filename}' corresponde ao padrão de nomeação de página.")
                
                # Se não for uma página potencial OU se tiver uma extensão que não seja de imagem (e não for uma URL dinâmica sem extensão)
                if not is_potential_page:
                    app.logger.debug(f"Imagem '{img_filename}' de {img_url} não parece ser uma página de capítulo. Pulando.")
                    continue
                
                # Se chegou aqui, é uma página potencial. Tentar baixar.
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
                
                # Determinar extensão final para salvar
                final_extension = '.jpg' # Padrão
                if content_type.startswith('image/jpeg'): final_extension = '.jpg'
                elif content_type.startswith('image/png'): final_extension = '.png'
                elif content_type.startswith('image/webp'): final_extension = '.webp'
                elif content_type.startswith('image/gif'): final_extension = '.gif'
                elif ext_part in ['.jpg', '.jpeg', '.png', '.webp', '.gif']: # Usa a extensão do URL se o content-type for genérico
                    final_extension = ext_part

                # Salvar com nome sequencial para manter a ordem de descoberta
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
        # else: (img_url era None)
            # app.logger.debug(f"URL de imagem não extraída da tag: {tag.get('src', str(tag)[:50])}")


    if not imagens_baixadas_paths:
        app.logger.warning(f"Nenhuma imagem de capítulo foi baixada de {url}.")
        flash("Nenhuma imagem de capítulo foi encontrada ou baixada (verifique os logs para detalhes).", "error")
        if os.path.exists(pasta_temp): shutil.rmtree(pasta_temp)
        return None

    # ... (O restante da função para processar com PIL, criar PDF, gerar thumbnail e limpar tmp permanece o mesmo da versão anterior robusta) ...
    # Certifique-se de que a lógica de abrir com PIL e criar PDF está como na resposta anterior.
    app.logger.info(f"Processando {len(imagens_baixadas_paths)} imagens baixadas com PIL...")
    imagens_pil = []
    for f_path in sorted(imagens_baixadas_paths): # Ordena pelos nomes 000.ext, 001.ext, etc.
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
    
    nome_pdf_arquivo = f"capitulo_{str(numero_capitulo).zfill(3)}.pdf" # Nome de PDF mais padronizado
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

@app.route("/excluir_capitulo/<path:manga>/<path:arquivo>", methods=["DELETE"])
def excluir_capitulo(manga, arquivo):
    if not manga or not arquivo:
        return jsonify({"success": False, "message": "Nome do mangá ou arquivo não fornecido."}), 400

    # Sanitizar minimamente para evitar manipulação excessiva, mas a validação principal é no caminho
    manga_seguro = os.path.normpath(manga)
    arquivo_seguro = os.path.normpath(arquivo)

    # Impedir que 'manga' ou 'arquivo' tentem sair do diretório base
    if manga_seguro.startswith("..") or "/" in manga_seguro or "\\" in manga_seguro or \
       arquivo_seguro.startswith("..") or "/" in arquivo_seguro or "\\" in arquivo_seguro:
        return jsonify({"success": False, "message": "Nome de mangá ou arquivo inválido."}), 400
    
    caminho_pasta_manga_base = os.path.abspath(BASE_COMICS)
    caminho_pdf_completo = os.path.abspath(os.path.join(BASE_COMICS, manga_seguro, arquivo_seguro))
    caminho_thumb_completo = os.path.abspath(os.path.join(BASE_COMICS, manga_seguro, arquivo_seguro.replace(".pdf", ".jpg")))

    # Validação de Segurança: Garantir que os caminhos estão dentro do BASE_COMICS
    if not caminho_pdf_completo.startswith(caminho_pasta_manga_base) or \
       not caminho_thumb_completo.startswith(caminho_pasta_manga_base):
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
             # Verificar se a pasta do mangá está vazia (exceto por capa.jpg) e se pode ser removida
            conteudo_pasta = os.listdir(os.path.join(BASE_COMICS, manga_seguro))
            # Filtra para remover 'capa.jpg' se existir e arquivos de sistema como '.DS_Store'
            conteudo_relevante = [item for item in conteudo_pasta if item.lower() != 'capa.jpg' and not item.startswith('.')]
            
            if not conteudo_relevante: # Se a pasta do mangá ficou vazia (ou só tem a capa)
                # Poderíamos optar por remover a pasta do mangá aqui se ela ficar vazia de capítulos.
                # Mas por agora, vamos deixar a pasta, ela pode ser excluída com a função de excluir mangá inteiro.
                app.logger.info(f"Pasta do mangá '{manga_seguro}' pode estar vazia de capítulos.")

            return jsonify({"success": True, "message": f"Capítulo '{arquivo_seguro.replace('.pdf', '')}' excluído com sucesso!"})
        else:
            return jsonify({"success": False, "message": "Arquivo do capítulo não encontrado."}), 404

    except Exception as e:
        app.logger.error(f"Erro ao excluir capítulo '{arquivo_seguro}' de '{manga_seguro}': {e}")
        return jsonify({"success": False, "message": f"Erro interno ao excluir o capítulo: {str(e)}"}), 500

@app.route("/excluir_manga/<path:nome_manga>", methods=["DELETE"])
def excluir_manga(nome_manga):
    if not nome_manga:
        return jsonify({"success": False, "message": "Nome do mangá não fornecido."}), 400

    manga_seguro = os.path.normpath(nome_manga)
    if manga_seguro.startswith("..") or "/" in manga_seguro or "\\" in manga_seguro :
        return jsonify({"success": False, "message": "Nome de mangá inválido."}), 400

    caminho_pasta_manga_base = os.path.abspath(BASE_COMICS)
    caminho_pasta_manga_completo = os.path.abspath(os.path.join(BASE_COMICS, manga_seguro))

    # Validação de Segurança
    if not caminho_pasta_manga_completo.startswith(caminho_pasta_manga_base) or caminho_pasta_manga_completo == caminho_pasta_manga_base: # Impede excluir a raiz
        app.logger.warning(f"Tentativa de acesso inválido para exclusão de mangá: '{manga_seguro}'")
        return jsonify({"success": False, "message": "Acesso negado."}), 403
    
    try:
        if os.path.exists(caminho_pasta_manga_completo) and os.path.isdir(caminho_pasta_manga_completo):
            shutil.rmtree(caminho_pasta_manga_completo) # Exclui a pasta e todo o seu conteúdo
            app.logger.info(f"Mangá excluído: {caminho_pasta_manga_completo}")
            
            # Opcional: Remover dos URLs salvos se existir
            urls_salvas = carregar_urls()
            if manga_seguro in urls_salvas:
                del urls_salvas[manga_seguro]
                salvar_urls(urls_salvas)
                app.logger.info(f"URL predefinida para '{manga_seguro}' removida.")

            return jsonify({"success": True, "message": f"Mangá '{manga_seguro}' e todos os seus capítulos foram excluídos com sucesso!"})
        else:
            app.logger.warning(f"Pasta do mangá não encontrada para exclusão: {caminho_pasta_manga_completo}")
            return jsonify({"success": False, "message": "Pasta do mangá não encontrada."}), 404
    except Exception as e:
        app.logger.error(f"Erro ao excluir o mangá '{manga_seguro}': {e}")
        return jsonify({"success": False, "message": f"Erro interno ao excluir o mangá: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)