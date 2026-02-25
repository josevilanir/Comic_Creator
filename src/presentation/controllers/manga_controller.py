"""
Manga Controller - Controller para gerenciamento de mangás isolado por usuário
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, g
from PIL import Image
import os
from src.presentation.decorators.auth_required import auth_required

manga_bp = Blueprint('manga', __name__)


@manga_bp.route('/biblioteca')
@auth_required
def biblioteca():
    """Lista todos os mangás da biblioteca do usuário"""
    container = current_app.container
    
    # Lista mangás passando user_id
    mangas = container.manga_repository.listar_todos(g.user_id)
    
    # Prepara dados para o template
    pastas = [{
        'nome': manga.nome,
        'tem_capa': manga.tem_capa,
        'capa_url': url_for('manga.visualizar_capa', nome_manga=manga.nome) if manga.tem_capa else None,
        'total_capitulos': manga.total_capitulos
    } for manga in mangas]
    
    return render_template('biblioteca.html', pastas=pastas)


@manga_bp.route('/capa/<nome_manga>')
@auth_required
def visualizar_capa(nome_manga):
    """Serve o arquivo de capa de um mangá isolado por usuário"""
    container = current_app.container
    
    # Busca mangá passando user_id
    manga = container.manga_repository.buscar_por_nome(g.user_id, nome_manga)
    if not manga or not manga.tem_capa:
        return 'Capa não encontrada', 404
    
    # Caminho da capa
    caminho_capa = os.path.join(manga.caminho, 'capa.jpg')
    
    if not os.path.exists(caminho_capa):
        return 'Arquivo de capa não encontrado', 404
    
    return send_file(caminho_capa, mimetype='image/jpeg')


@manga_bp.route('/upload_capa/<nome_manga>', methods=['POST'])
@auth_required
def upload_capa(nome_manga):
    """Faz upload de capa para um mangá isolado"""
    container = current_app.container
    
    manga = container.manga_repository.buscar_por_nome(g.user_id, nome_manga)
    if not manga:
        flash('Mangá não encontrado.', 'error')
        return redirect(url_for('manga.biblioteca'))
    
    if 'capa' not in request.files:
        flash('Nenhum arquivo enviado.', 'error')
        return redirect(url_for('manga.biblioteca'))
    
    file = request.files['capa']
    if file.filename == '':
        flash('Arquivo sem nome.', 'error')
        return redirect(url_for('manga.biblioteca'))
    
    extensoes_permitidas = {'png', 'jpg', 'jpeg', 'webp'}
    if '.' not in file.filename or \
       file.filename.rsplit('.', 1)[1].lower() not in extensoes_permitidas:
        flash('Formato inválido.', 'error')
        return redirect(url_for('manga.biblioteca'))
    
    try:
        img = Image.open(file.stream).convert('RGB')
        caminho_capa = os.path.join(manga.caminho, 'capa.jpg')
        img.save(caminho_capa, 'JPEG', quality=90)
        flash(f'Capa atualizada para {nome_manga}.', 'success')
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('manga.biblioteca'))


@manga_bp.route('/excluir/<nome_manga>', methods=['DELETE'])
@auth_required
def excluir_manga(nome_manga):
    """Exclui um mangá e todos seus capítulos"""
    from flask import jsonify
    container = current_app.container
    
    try:
        if not container.manga_repository.existe(g.user_id, nome_manga):
            return jsonify({'success': False, 'message': 'Mangá não encontrado.'}), 404
        
        if container.manga_repository.deletar(g.user_id, nome_manga):
            # Tenta remover URL salva isolada
            try:
                container.url_repository.deletar(g.user_id, nome_manga)
            except: pass
            
            return jsonify({
                'success': True,
                'message': f"Mangá '{nome_manga}' excluído."
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao excluir mangá.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f"Erro: {str(e)}"}), 500
