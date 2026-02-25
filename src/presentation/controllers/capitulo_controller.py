"""
Capitulo Controller - Controller para gerenciamento de capítulos
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, jsonify, g
import os
from src.presentation.decorators.auth_required import auth_required

capitulo_bp = Blueprint('capitulo', __name__)


@capitulo_bp.route('/<nome_manga>')
def listar_capitulos(nome_manga):
    """Lista capítulos de um mangá"""
    container = current_app.container
    
    # Verifica se mangá existe
    manga = container.manga_repository.buscar_por_nome(nome_manga)
    if not manga:
        flash(f"Mangá '{nome_manga}' não encontrado.", 'error')
        return redirect(url_for('manga.biblioteca'))
    
    # Ordem de listagem
    ordem = request.args.get('ordem', 'asc')
    
    # Lista capítulos
    capitulos = container.capitulo_repository.listar_por_manga(nome_manga, ordem=ordem)
    
    # Prepara dados para template
    arquivos = []
    for cap in capitulos:
        arquivos.append(cap.nome_arquivo)
    
    return render_template(
        'lista_pdfs.html',
        nome_pasta=nome_manga,
        arquivos=arquivos,
        ordem=ordem,
        lidos=[]
    )


@capitulo_bp.route('/visualizar/<nome_manga>/<nome_arquivo>')
def visualizar_pdf(nome_manga, nome_arquivo):
    """Serve arquivo PDF de um capítulo"""
    container = current_app.container
    
    # Valida segurança (evita path traversal)
    if '..' in nome_manga or '..' in nome_arquivo:
        return 'Acesso negado', 403
    
    # Busca mangá
    manga = container.manga_repository.buscar_por_nome(nome_manga)
    if not manga:
        return 'Mangá não encontrado', 404
    
    # Caminho do PDF
    caminho_pdf = os.path.join(manga.caminho, nome_arquivo)
    
    if not os.path.exists(caminho_pdf):
        return 'Arquivo não encontrado', 404
    
    return send_file(caminho_pdf, mimetype='application/pdf')


@capitulo_bp.route('/thumbnail/<nome_manga>/<nome_arquivo>')
def visualizar_thumbnail(nome_manga, nome_arquivo):
    """Serve thumbnail de um capítulo"""
    container = current_app.container
    
    # Valida segurança
    if '..' in nome_manga or '..' in nome_arquivo:
        return 'Acesso negado', 403
    
    # Busca mangá
    manga = container.manga_repository.buscar_por_nome(nome_manga)
    if not manga:
        return 'Mangá não encontrado', 404
    
    # Caminho do thumbnail
    nome_thumb = nome_arquivo.replace('.pdf', '.jpg')
    caminho_thumb = os.path.join(manga.caminho, nome_thumb)
    
    if not os.path.exists(caminho_thumb):
        # Se não existe, tenta gerar
        try:
            caminho_pdf = os.path.join(manga.caminho, nome_arquivo)
            if os.path.exists(caminho_pdf):
                container.thumbnail_service.gerar_thumbnail_auto(caminho_pdf, manga.caminho)
        except Exception:
            pass
    
    if os.path.exists(caminho_thumb):
        return send_file(caminho_thumb, mimetype='image/jpeg')
    
    return 'Thumbnail não disponível', 404


@capitulo_bp.route('/excluir/<nome_manga>/<nome_arquivo>', methods=['DELETE'])
def excluir_capitulo(nome_manga, nome_arquivo):
    """Exclui um capítulo específico"""
    container = current_app.container
    
    try:
        # Valida segurança
        if '..' in nome_manga or '..' in nome_arquivo:
            return jsonify({
                'success': False,
                'message': 'Acesso negado.'
            }), 403
        
        # Deleta capítulo
        if container.capitulo_repository.deletar(nome_manga, nome_arquivo):
            return jsonify({
                'success': True,
                'message': f"Capítulo '{nome_arquivo.replace('.pdf', '')}' excluído com sucesso!"
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Capítulo não encontrado.'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erro: {str(e)}"
        }), 500


@capitulo_bp.route('/lido/<nome_manga>/<nome_arquivo>', methods=['POST'])
@auth_required
def toggle_lido(nome_manga, nome_arquivo):
    """Alterna estado de leitura de um capítulo"""
    if '..' in nome_manga or '..' in nome_arquivo:
        from src.presentation.api.jsend import fail
        return fail({'path': 'Acesso negado.'}, 403)

    try:
        from src.presentation.api.jsend import success, error
        container = current_app.container
        is_read = container.user_data_repository.toggle_read(g.user_id, nome_manga, nome_arquivo)

        return success({
            'lido': is_read,
            'message': 'Marcado como lido!' if is_read else 'Marcado como não lido.'
        })
    except Exception as e:
        from src.presentation.api.jsend import error
        return error(str(e), 'TOGGLE_LIDO_ERROR')
