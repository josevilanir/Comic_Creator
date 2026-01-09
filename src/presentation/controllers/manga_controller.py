"""
Manga Controller - Controller para gerenciamento de mangás
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import os

manga_bp = Blueprint('manga', __name__)


@manga_bp.route('/biblioteca')
def biblioteca():
    """Lista todos os mangás da biblioteca"""
    container = current_app.container
    
    # Lista mangás do repositório
    mangas = container.manga_repository.listar_todos()
    
    # Prepara dados para o template
    pastas = []
    for manga in mangas:
        pastas.append({
            'nome': manga.nome,
            'tem_capa': manga.tem_capa,
            'capa_url': url_for('manga.visualizar_capa', nome_manga=manga.nome) if manga.tem_capa else None,
            'total_capitulos': manga.total_capitulos
        })
    
    return render_template('biblioteca.html', pastas=pastas)


@manga_bp.route('/capa/<nome_manga>')
def visualizar_capa(nome_manga):
    """Serve o arquivo de capa de um mangá"""
    container = current_app.container
    
    # Busca mangá
    manga = container.manga_repository.buscar_por_nome(nome_manga)
    if not manga or not manga.tem_capa:
        return 'Capa não encontrada', 404
    
    # Caminho da capa
    caminho_capa = os.path.join(manga.caminho, 'capa.jpg')
    
    if not os.path.exists(caminho_capa):
        return 'Arquivo de capa não encontrado', 404
    
    return send_file(caminho_capa, mimetype='image/jpeg')


@manga_bp.route('/upload_capa/<nome_manga>', methods=['POST'])
def upload_capa(nome_manga):
    """Faz upload de capa para um mangá"""
    container = current_app.container
    
    # Verifica se mangá existe
    manga = container.manga_repository.buscar_por_nome(nome_manga)
    if not manga:
        flash('Mangá não encontrado.', 'error')
        return redirect(url_for('manga.biblioteca'))
    
    # Verifica se arquivo foi enviado
    if 'capa' not in request.files:
        flash('Nenhum arquivo enviado.', 'error')
        return redirect(url_for('manga.biblioteca'))
    
    file = request.files['capa']
    
    if file.filename == '':
        flash('Arquivo sem nome.', 'error')
        return redirect(url_for('manga.biblioteca'))
    
    # Valida extensão
    extensoes_permitidas = {'png', 'jpg', 'jpeg', 'webp'}
    if '.' not in file.filename or \
       file.filename.rsplit('.', 1)[1].lower() not in extensoes_permitidas:
        flash('Formato de arquivo inválido. Use PNG, JPG, JPEG ou WEBP.', 'error')
        return redirect(url_for('manga.biblioteca'))
    
    try:
        # Abre imagem e converte para RGB
        img = Image.open(file.stream).convert('RGB')
        
        # Salva como capa.jpg
        caminho_capa = os.path.join(manga.caminho, 'capa.jpg')
        img.save(caminho_capa, 'JPEG', quality=90)
        
        flash(f'Capa atualizada para {nome_manga}.', 'success')
        
    except Exception as e:
        flash(f'Erro ao processar imagem: {str(e)}', 'error')
    
    return redirect(url_for('manga.biblioteca'))


@manga_bp.route('/excluir/<nome_manga>', methods=['DELETE'])
def excluir_manga(nome_manga):
    """Exclui um mangá e todos seus capítulos"""
    from flask import jsonify
    
    container = current_app.container
    
    try:
        # Verifica se existe
        if not container.manga_repository.existe(nome_manga):
            return jsonify({
                'success': False,
                'message': 'Mangá não encontrado.'
            }), 404
        
        # Deleta do repositório
        if container.manga_repository.deletar(nome_manga):
            # Remove URL salva se existir
            container.url_repository.deletar(nome_manga)
            
            return jsonify({
                'success': True,
                'message': f"Mangá '{nome_manga}' e todos os seus capítulos foram excluídos."
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao excluir mangá.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erro: {str(e)}"
        }), 500