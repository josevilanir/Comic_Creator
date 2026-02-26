"""
Capitulo Controller - Controller para gerenciamento de capítulos
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, jsonify, g, Response
import os
from src.presentation.decorators.auth_required import auth_required

capitulo_bp = Blueprint('capitulo', __name__)


@capitulo_bp.route('/<nome_manga>')
@auth_required
def listar_capitulos(nome_manga):
    """Lista capítulos de um mangá"""
    container = current_app.container
    
    # Verifica se mangá existe
    manga = container.manga_repository.buscar_por_nome(g.user_id, nome_manga)
    if not manga:
        flash(f"Mangá '{nome_manga}' não encontrado.", 'error')
        return redirect(url_for('manga.biblioteca'))
    
    # Ordem de listagem
    ordem = request.args.get('ordem', 'asc')
    
    # Lista capítulos
    capitulos = container.capitulo_repository.listar_por_manga(g.user_id, nome_manga, ordem=ordem)
    
    # Prepara dados para template
    arquivos = [cap.nome_arquivo for cap in capitulos]
    
    return render_template(
        'lista_pdfs.html',
        nome_pasta=nome_manga,
        arquivos=arquivos,
        ordem=ordem,
        lidos=[]
    )


@capitulo_bp.route('/visualizar/<nome_manga>/<nome_arquivo>')
@auth_required
def visualizar_pdf(nome_manga, nome_arquivo):
    """Serve arquivo PDF de um capítulo."""
    container = current_app.container

    if '..' in nome_manga or '..' in nome_arquivo:
        return 'Acesso negado', 403

    # Modo S3: redireciona para URL assinada temporária
    if getattr(container, 's3_service', None):
        key = f"user_{g.user_id}/{nome_manga}/{nome_arquivo}"
        url = container.s3_service.get_presigned_url(key)
        return redirect(url)

    # Modo filesystem
    manga = container.manga_repository.buscar_por_nome(g.user_id, nome_manga)
    if not manga:
        return 'Mangá não encontrado', 404
    caminho_pdf = os.path.join(manga.caminho, nome_arquivo)
    if not os.path.exists(caminho_pdf):
        return 'Arquivo não encontrado', 404
    return send_file(caminho_pdf, mimetype='application/pdf')


@capitulo_bp.route('/thumbnail/<nome_manga>/<nome_arquivo>')
@auth_required
def visualizar_thumbnail(nome_manga, nome_arquivo):
    """Serve thumbnail de um capítulo."""
    container = current_app.container

    if '..' in nome_manga or '..' in nome_arquivo:
        return 'Acesso negado', 403

    # Modo S3: redireciona para URL assinada temporária
    if getattr(container, 's3_service', None):
        nome_thumb = nome_arquivo.replace('.pdf', '.jpg')
        key = f"user_{g.user_id}/{nome_manga}/{nome_thumb}"
        if not container.s3_service.object_exists(key):
            return 'Thumbnail não disponível', 404
        url = container.s3_service.get_presigned_url(key)
        return redirect(url)

    # Modo filesystem
    manga = container.manga_repository.buscar_por_nome(g.user_id, nome_manga)
    if not manga:
        return 'Mangá não encontrado', 404
    nome_thumb = nome_arquivo.replace('.pdf', '.jpg')
    caminho_thumb = os.path.join(manga.caminho, nome_thumb)
    if not os.path.exists(caminho_thumb):
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
@auth_required
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
        
        # Deleta capítulo passando user_id
        if container.capitulo_repository.deletar(g.user_id, nome_manga, nome_arquivo):
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
