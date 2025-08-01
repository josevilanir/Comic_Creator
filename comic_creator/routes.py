import os
import shutil
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app

from .downloader import baixar_capitulo_para_pdf
from .utils import (
    carregar_urls,
    salvar_urls,
    limpar_sufixo_manga_pt_br,
    extrair_nome_manga,
)

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    urls_salvas = carregar_urls()
    base_url_for_template = request.args.get('base_url', '')

    if request.method == 'POST':
        acao = request.form.get('acao')
        base_url_for_template = request.form.get('base_url', base_url_for_template)

        if acao == 'salvar_url':
            nova_url = request.form.get('nova_url', '').strip()
            nome_manga_key = request.form.get('nome_manga', '').strip()
            if nova_url and nome_manga_key:
                urls_salvas[nome_manga_key] = nova_url
                salvar_urls(urls_salvas)
                flash(f"URL para '{nome_manga_key}' salva com sucesso!", 'success')
            else:
                flash('Nome do mang\u00e1 e URL s\u00e3o obrigat\u00f3rios para salvar.', 'error')
            return redirect(url_for('main.index', base_url=nova_url if (nova_url and nome_manga_key) else base_url_for_template))

        elif acao == 'remover_url':
            nome_manga_key = request.form.get('nome_manga', '').strip()
            if nome_manga_key in urls_salvas:
                urls_salvas.pop(nome_manga_key)
                salvar_urls(urls_salvas)
                flash(f"URL de '{nome_manga_key}' removida com sucesso!", 'success')
            else:
                flash(f"URL para '{nome_manga_key}' n\u00e3o encontrada.", 'error')
            return redirect(url_for('main.index', base_url=base_url_for_template))

        elif acao in {'baixar_manual', 'baixar_predefinida'}:
            base_url_from_form = request.form.get('base_url', '').strip()
            capitulo_str = request.form.get('capitulo', '').strip()
            nome_manga_key_from_form = request.form.get('nome_manga', '').strip()
            base_url_for_template = base_url_from_form

            if not (base_url_from_form and capitulo_str and capitulo_str.isdigit()):
                flash('Dados inv\u00e1lidos. Verifique a URL base e o n\u00famero do cap\u00edtulo.', 'error')
                return render_template('index.html', urls_salvas=urls_salvas, base_url=base_url_for_template)

            url_construction_suffix = ''
            string_to_check_for_ptbr = nome_manga_key_from_form + ' ' + base_url_from_form if acao == 'baixar_predefinida' and nome_manga_key_from_form else base_url_from_form
            if 'manga-pt-br' in string_to_check_for_ptbr.lower():
                url_construction_suffix = '-pt-br'

            final_chapter_page_url = f"{base_url_from_form}{capitulo_str}{url_construction_suffix}/"

            url_for_folder_name_extraction = base_url_from_form
            if url_for_folder_name_extraction.lower().endswith('capitulo-'):
                url_for_folder_name_extraction = url_for_folder_name_extraction[:-len('capitulo-')]
            elif url_for_folder_name_extraction.lower().endswith('chap-'):
                url_for_folder_name_extraction = url_for_folder_name_extraction[:-len('chap-')]

            nome_manga_para_pasta_bruto = extrair_nome_manga(url_for_folder_name_extraction)

            if acao == 'baixar_predefinida' and nome_manga_key_from_form:
                nome_manga_para_pasta = nome_manga_key_from_form
            else:
                nome_manga_para_pasta = nome_manga_para_pasta_bruto

            if nome_manga_para_pasta and nome_manga_para_pasta != 'Manga Desconhecido':
                nome_manga_para_pasta_limpo = limpar_sufixo_manga_pt_br(nome_manga_para_pasta)
                if not nome_manga_para_pasta_limpo and nome_manga_para_pasta_bruto and nome_manga_para_pasta_bruto != 'Manga Desconhecido':
                    nome_manga_para_pasta = nome_manga_para_pasta_bruto
                elif nome_manga_para_pasta_limpo:
                    nome_manga_para_pasta = nome_manga_para_pasta_limpo
                elif not nome_manga_para_pasta_limpo and (not nome_manga_para_pasta_bruto or nome_manga_para_pasta_bruto == 'Manga Desconhecido'):
                    nome_manga_para_pasta = 'Manga_Sem_Nome_Definido'

            current_app.logger.info(f"Tentando baixar: Manga '{nome_manga_para_pasta}', Capitulo '{capitulo_str}'. URL: '{final_chapter_page_url}'")
            resultado_download = baixar_capitulo_para_pdf(final_chapter_page_url, nome_manga_para_pasta, capitulo_str)

            if resultado_download:
                flash(f"Download do cap\u00edtulo {capitulo_str} de '{nome_manga_para_pasta}' conclu\u00eddo! PDF: {resultado_download}", 'success')

            return redirect(url_for('main.index', base_url=base_url_from_form))

        return render_template('index.html', urls_salvas=urls_salvas, base_url=base_url_for_template)

    return render_template('index.html', urls_salvas=urls_salvas, base_url=base_url_for_template)


@bp.route('/biblioteca')
def biblioteca():
    base_dir = current_app.config['BASE_COMICS']
    pastas = []
    for item in os.listdir(base_dir):
        caminho_completo_item = os.path.join(base_dir, item)
        if os.path.isdir(caminho_completo_item):
            capa_path = os.path.join(caminho_completo_item, 'capa.jpg')
            tem_capa = os.path.exists(capa_path)
            pastas.append({
                'nome': item,
                'tem_capa': tem_capa,
                'capa_url': url_for('main.visualizar_pdf', manga=item, arquivo='capa.jpg') if tem_capa else None
            })
    pastas = sorted(pastas, key=lambda p: p['nome'].lower())
    return render_template('biblioteca.html', pastas=pastas)


@bp.route('/pasta/<path:nome_pasta>')
def listar_pasta(nome_pasta):
    base_dir = current_app.config['BASE_COMICS']
    pasta = os.path.join(base_dir, nome_pasta)
    if not os.path.isdir(pasta):
        flash(f"Pasta '{nome_pasta}' n\u00e3o encontrada.", 'error')
        return redirect(url_for('main.biblioteca'))

    ordem = request.args.get('ordem', 'asc')
    try:
        arquivos = sorted(
            [f for f in os.listdir(pasta) if f.lower().endswith('.pdf')],
            key=lambda nome: int(''.join(filter(str.isdigit, os.path.splitext(nome)[0])) or 0),
            reverse=(ordem == 'desc')
        )
    except ValueError:
        current_app.logger.warning(f"Falha na ordena\u00e7\u00e3o num\u00e9rica para {nome_pasta}, usando alfab\u00e9tica.")
        arquivos = sorted(
            [f for f in os.listdir(pasta) if f.lower().endswith('.pdf')],
            reverse=(ordem == 'desc')
        )

    return render_template('lista_pdfs.html', nome_pasta=nome_pasta, arquivos=arquivos, ordem=ordem)


@bp.route('/visualizar/<path:manga>/<path:arquivo>')
def visualizar_pdf(manga, arquivo):
    base_dir = current_app.config['BASE_COMICS']
    manga_seguro = os.path.normpath(manga)
    arquivo_seguro = os.path.normpath(arquivo)
    if manga_seguro.startswith('..') or arquivo_seguro.startswith('..') or '/' in manga_seguro or '\\' in manga_seguro:
        current_app.logger.warning(f"Tentativa de acesso a caminho inv\u00e1lido: manga='{manga}', arquivo='{arquivo}'")
        return 'Acesso negado a caminho inv\u00e1lido.', 403

    caminho_completo = os.path.abspath(os.path.join(base_dir, manga_seguro, arquivo_seguro))
    base_comics_abs = os.path.abspath(base_dir)
    if not caminho_completo.startswith(base_comics_abs):
        current_app.logger.warning(f"Tentativa de acesso fora do diret\u00f3rio base: '{caminho_completo}'")
        return 'Acesso negado.', 403
    if os.path.exists(caminho_completo) and os.path.isfile(caminho_completo):
        return send_file(caminho_completo)
    current_app.logger.error(f"Arquivo n\u00e3o encontrado em visualizar_pdf: {caminho_completo}")
    return 'Arquivo n\u00e3o encontrado', 404


@bp.route('/upload_capa/<path:nome_pasta>', methods=['POST'])
def upload_capa(nome_pasta):
    base_dir = current_app.config['BASE_COMICS']
    nome_pasta_seguro = os.path.normpath(nome_pasta)
    if nome_pasta_seguro.startswith('..') or '/' in nome_pasta_seguro or '\\' in nome_pasta_seguro:
        flash('Nome de pasta inv\u00e1lido.', 'error')
        return redirect(url_for('main.biblioteca'))

    pasta_destino = os.path.abspath(os.path.join(base_dir, nome_pasta_seguro))
    base_comics_abs = os.path.abspath(base_dir)
    if not pasta_destino.startswith(base_comics_abs):
        flash('Acesso negado \u00e0 pasta.', 'error')
        return redirect(url_for('main.biblioteca'))
    if not os.path.exists(pasta_destino) or not os.path.isdir(pasta_destino):
        flash('Pasta do mang\u00e1 n\u00e3o encontrada.', 'error')
        return redirect(url_for('main.biblioteca'))
    if 'capa' not in request.files:
        flash('Nenhum arquivo de capa enviado.', 'error')
        return redirect(url_for('main.biblioteca'))
    file = request.files['capa']
    if file.filename == '':
        flash('Arquivo de capa sem nome.', 'error')
        return redirect(url_for('main.biblioteca'))
    extensoes_permitidas = {'png', 'jpg', 'jpeg', 'webp'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in extensoes_permitidas:
        flash('Formato de arquivo de capa inv\u00e1lido. Use PNG, JPG, JPEG ou WEBP.', 'error')
        return redirect(url_for('main.biblioteca'))
    try:
        caminho_capa_final = os.path.join(pasta_destino, 'capa.jpg')
        Image.open(file.stream).convert('RGB').save(caminho_capa_final, 'JPEG')
        flash(f'Capa atualizada para {nome_pasta_seguro}.', 'success')
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar capa para {nome_pasta_seguro}: {e}")
        flash('Erro ao processar ou salvar a imagem da capa.', 'error')
    return redirect(url_for('main.biblioteca'))


@bp.route('/excluir_capitulo/<path:manga>/<path:arquivo>', methods=['DELETE'])
def excluir_capitulo(manga, arquivo):
    base_dir = current_app.config['BASE_COMICS']
    manga_seguro = os.path.normpath(manga)
    arquivo_seguro = os.path.normpath(arquivo)
    if (manga_seguro.startswith('..') or '/' in manga_seguro or '\\' in manga_seguro or
            arquivo_seguro.startswith('..') or '/' in arquivo_seguro or '\\' in arquivo_seguro):
        return jsonify({'success': False, 'message': 'Nome de mang\u00e1 ou arquivo inv\u00e1lido.'}), 400

    caminho_pasta_manga_base = os.path.abspath(base_dir)
    caminho_pdf_completo = os.path.abspath(os.path.join(base_dir, manga_seguro, arquivo_seguro))

    nome_base_arquivo, _ = os.path.splitext(arquivo_seguro)
    caminho_thumb_completo = os.path.abspath(os.path.join(base_dir, manga_seguro, nome_base_arquivo + '.jpg'))

    if not caminho_pdf_completo.startswith(caminho_pasta_manga_base) or (
        os.path.exists(caminho_thumb_completo) and not caminho_thumb_completo.startswith(caminho_pasta_manga_base)):
        current_app.logger.warning(f"Tentativa de acesso inv\u00e1lido para exclus\u00e3o: Manga '{manga_seguro}', Arquivo '{arquivo_seguro}'")
        return jsonify({'success': False, 'message': 'Acesso negado.'}), 403
    try:
        pdf_excluido = False
        if os.path.exists(caminho_pdf_completo) and os.path.isfile(caminho_pdf_completo):
            os.remove(caminho_pdf_completo)
            pdf_excluido = True
            current_app.logger.info(f"Cap\u00edtulo PDF exclu\u00eddo: {caminho_pdf_completo}")
        else:
            current_app.logger.warning(f"Cap\u00edtulo PDF n\u00e3o encontrado para exclus\u00e3o: {caminho_pdf_completo}")
        if os.path.exists(caminho_thumb_completo) and os.path.isfile(caminho_thumb_completo):
            os.remove(caminho_thumb_completo)
            current_app.logger.info(f"Thumbnail do cap\u00edtulo exclu\u00eddo: {caminho_thumb_completo}")
        if pdf_excluido:
            return jsonify({'success': True, 'message': f"Cap\u00edtulo '{arquivo_seguro.replace('.pdf', '')}' exclu\u00eddo com sucesso!"})
        else:
            return jsonify({'success': False, 'message': 'Arquivo do cap\u00edtulo n\u00e3o encontrado.'}), 404
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir cap\u00edtulo '{arquivo_seguro}' de '{manga_seguro}': {e}")
        return jsonify({'success': False, 'message': f"Erro interno ao excluir o cap\u00edtulo: {str(e)}"}), 500


@bp.route('/excluir_manga/<path:nome_manga>', methods=['DELETE'])
def excluir_manga(nome_manga):
    base_dir = current_app.config['BASE_COMICS']
    manga_seguro = os.path.normpath(nome_manga)
    if manga_seguro.startswith('..') or '/' in manga_seguro or '\\' in manga_seguro:
        return jsonify({'success': False, 'message': 'Nome de mang\u00e1 inv\u00e1lido.'}), 400

    caminho_pasta_manga_base = os.path.abspath(base_dir)
    caminho_pasta_manga_completo = os.path.abspath(os.path.join(base_dir, manga_seguro))
    if not caminho_pasta_manga_completo.startswith(caminho_pasta_manga_base) or caminho_pasta_manga_completo == caminho_pasta_manga_base:
        current_app.logger.warning(f"Tentativa de acesso inv\u00e1lido para exclus\u00e3o de mang\u00e1: '{manga_seguro}'")
        return jsonify({'success': False, 'message': 'Acesso negado.'}), 403
    try:
        if os.path.exists(caminho_pasta_manga_completo) and os.path.isdir(caminho_pasta_manga_completo):
            shutil.rmtree(caminho_pasta_manga_completo)
            current_app.logger.info(f"Mang\u00e1 exclu\u00eddo: {caminho_pasta_manga_completo}")
            urls_salvas = carregar_urls()
            chave_manga_limpa = limpar_sufixo_manga_pt_br(manga_seguro.replace('_', ' ').title())
            chave_manga_original = manga_seguro
            chaves_para_tentar_remover = {chave_manga_original, chave_manga_limpa}
            for chave in chaves_para_tentar_remover:
                if chave in urls_salvas:
                    del urls_salvas[chave]
                    salvar_urls(urls_salvas)
                    current_app.logger.info(f"URL predefinida para '{chave}' removida.")
            return jsonify({'success': True, 'message': f"Mang\u00e1 '{manga_seguro}' e todos os seus cap\u00edtulos foram exclu\u00eddos."})
        else:
            current_app.logger.warning(f"Pasta do mang\u00e1 n\u00e3o encontrada para exclus\u00e3o: {caminho_pasta_manga_completo}")
            return jsonify({'success': False, 'message': 'Pasta do mang\u00e1 n\u00e3o encontrada.'}), 404
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir o mang\u00e1 '{manga_seguro}': {e}")
        return jsonify({'success': False, 'message': f"Erro interno ao excluir o mang\u00e1: {str(e)}"}), 500
