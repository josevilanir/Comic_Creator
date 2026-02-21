"""
API REST Routes - Endpoints JSON para o frontend React
"""
from flask import Blueprint, jsonify, request, current_app, url_for

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/library', methods=['GET'])
def get_library():
    """Lista todos os mangás (JSON)"""
    container = current_app.container
    mangas = container.manga_repository.listar_todos()
    
    resultado = []
    for manga in mangas:
        resultado.append({
            'nome': manga.nome,
            'tem_capa': manga.tem_capa,
            'capa_url': url_for('manga.visualizar_capa', nome_manga=manga.nome, _external=True) if manga.tem_capa else None,
            'total_capitulos': manga.total_capitulos
        })
    
    return jsonify(resultado)


@api_bp.route('/urls', methods=['GET'])
def get_urls():
    """Lista URLs salvas (JSON)"""
    container = current_app.container
    urls_entities = container.url_repository.listar_todas()
    
    # Converte para dicionário {nome: url}
    urls_dict = {url.nome_manga: url.url_base for url in urls_entities}
    
    return jsonify(urls_dict)


@api_bp.route('/urls', methods=['POST'])
def save_url():
    """Salva nova URL"""
    data = request.json
    nome = data.get('nome')
    url = data.get('url')
    
    if not nome or not url:
        return jsonify({'success': False, 'message': 'Nome e URL obrigatórios'}), 400
    
    try:
        from src.domain.entities import URLSalva
        container = current_app.container
        
        url_salva = URLSalva(nome_manga=nome, url_base=url)
        container.url_repository.salvar(url_salva)
        
        return jsonify({'success': True, 'message': 'URL salva com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/urls', methods=['DELETE'])
def delete_url():
    """Remove URL salva"""
    data = request.json
    nome = data.get('nome')
    
    if not nome:
        return jsonify({'success': False, 'message': 'Nome obrigatório'}), 400
    
    try:
        container = current_app.container
        sucesso = container.url_repository.deletar(nome)
        
        if sucesso:
            return jsonify({'success': True, 'message': 'URL removida!'})
        else:
            return jsonify({'success': False, 'message': 'URL não encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/download', methods=['POST'])
def download_chapter():
    """Baixa capítulo"""
    data = request.json
    base_url = data.get('base_url')
    capitulo = data.get('capitulo')
    nome_manga = data.get('nome_manga')
    
    if not all([base_url, capitulo, nome_manga]):
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
    
    try:
        container = current_app.container
        
        # Importa DTO e use case
        from src.application.use_cases import BaixarCapituloDTO
        import re
        
        # Limpa nome do mangá
        def limpar_sufixo(nome: str) -> str:
            padrao = r'[-_\s]*(manga[-_\s]*)?pt[-_\s]*br$'
            return re.sub(padrao, '', nome, flags=re.IGNORECASE).strip()
        
        nome_limpo = limpar_sufixo(nome_manga)
        
        url_completa = construir_url_capitulo_correta(base_url, int(capitulo))
        
        current_app.logger.info(f"URL construída: {url_completa}")
        
        # Cria DTO
        dto = BaixarCapituloDTO(
            url_capitulo=url_completa,
            nome_manga=nome_limpo,
            numero_capitulo=int(capitulo),
            sobrescrever=False
        )
        
        # Executa download
        resultado = container.baixar_capitulo_use_case.executar(dto)
        
        if resultado.sucesso:
            return jsonify({'success': True, 'message': resultado.mensagem})
        else:
            return jsonify({'success': False, 'message': resultado.mensagem}), 400
            
    except Exception as e:
        current_app.logger.exception(f"Erro no download: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@api_bp.route('/library/<nome_manga>', methods=['DELETE'])
def delete_manga(nome_manga):
    """
    Deleta um mangá e todos os seus capítulos.

    Params:
        nome_manga: Nome do mangá (URL encoded)
    """
    from urllib.parse import unquote
    nome_decodificado = unquote(nome_manga)

    try:
        container = current_app.container

        if not container.manga_repository.existe(nome_decodificado):
            return jsonify({'success': False, 'message': 'Mangá não encontrado.'}), 404

        if container.manga_repository.deletar(nome_decodificado):
            # Remove URL salva associada, se existir
            try:
                container.url_repository.deletar(nome_decodificado)
            except Exception:
                pass  # URL pode não existir — não é erro crítico

            current_app.logger.info(f"Mangá deletado via API: {nome_decodificado}")
            return jsonify({
                'success': True,
                'message': f"Mangá '{nome_decodificado}' e todos os seus capítulos foram excluídos."
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao excluir mangá.'}), 500

    except Exception as e:
        current_app.logger.exception(f"Erro ao deletar mangá '{nome_decodificado}': {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@api_bp.route('/library/<nome_manga>/<nome_arquivo>', methods=['DELETE'])
def delete_capitulo(nome_manga, nome_arquivo):
    """
    Deleta um capítulo específico de um mangá.

    Params:
        nome_manga:   Nome do mangá (URL encoded)
        nome_arquivo: Nome do arquivo PDF (URL encoded)
    """
    from urllib.parse import unquote

    nome_decodificado  = unquote(nome_manga)
    arquivo_decodificado = unquote(nome_arquivo)

    # Bloqueia path traversal
    if '..' in nome_decodificado or '..' in arquivo_decodificado:
        return jsonify({'success': False, 'message': 'Acesso negado.'}), 403

    try:
        container = current_app.container

        # Verifica se o mangá existe antes de tentar deletar
        if not container.manga_repository.existe(nome_decodificado):
            return jsonify({'success': False, 'message': 'Mangá não encontrado.'}), 404

        # Deleta via repositório (remove PDF + thumbnail automaticamente)
        if container.capitulo_repository.deletar(nome_decodificado, arquivo_decodificado):
            current_app.logger.info(
                f"Capítulo deletado via API: {nome_decodificado}/{arquivo_decodificado}"
            )
            return jsonify({
                'success': True,
                'message': f"Capítulo '{arquivo_decodificado.replace('.pdf', '')}' excluído com sucesso!"
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Capítulo não encontrado no disco.'
            }), 404

    except Exception as e:
        current_app.logger.exception(
            f"Erro ao deletar capítulo '{arquivo_decodificado}' de '{nome_decodificado}': {e}"
        )
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@api_bp.route('/library/<nome_manga>/capa', methods=['POST'])
def upload_capa(nome_manga):
    """
    Faz upload de imagem de capa para um mangá.

    Body: multipart/form-data com campo 'capa' (arquivo de imagem)
    Params:
        nome_manga: Nome do mangá (URL encoded)
    """
    from urllib.parse import unquote
    from PIL import Image

    nome_decodificado = unquote(nome_manga)

    try:
        container = current_app.container

        manga = container.manga_repository.buscar_por_nome(nome_decodificado)
        if not manga:
            return jsonify({'success': False, 'message': 'Mangá não encontrado.'}), 404

        if 'capa' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado.'}), 400

        file = request.files['capa']

        if file.filename == '':
            return jsonify({'success': False, 'message': 'Arquivo sem nome.'}), 400

        extensoes_permitidas = {'png', 'jpg', 'jpeg', 'webp'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in extensoes_permitidas:
            return jsonify({
                'success': False,
                'message': 'Formato inválido. Use PNG, JPG, JPEG ou WEBP.'
            }), 400

        # Converte para JPEG e salva como capa.jpg
        import os
        img = Image.open(file.stream).convert('RGB')
        caminho_capa = os.path.join(manga.caminho, 'capa.jpg')
        img.save(caminho_capa, 'JPEG', quality=90)

        current_app.logger.info(f"Capa atualizada via API: {nome_decodificado}")

        # Retorna a nova URL da capa para atualização imediata no frontend
        nova_url = url_for('manga.visualizar_capa', nome_manga=nome_decodificado, _external=True)
        return jsonify({
            'success': True,
            'message': f"Capa de '{nome_decodificado}' atualizada com sucesso!",
            'capa_url': nova_url
        })

    except Exception as e:
        current_app.logger.exception(f"Erro ao fazer upload de capa para '{nome_decodificado}': {e}")
        return jsonify({'success': False, 'message': f'Erro ao processar imagem: {str(e)}'}), 500

def construir_url_capitulo_correta(base_url: str, numero_capitulo: int) -> str:
    """
    Constrói URL correta do capítulo.
    
    Exemplos:
        Input: "https://site.com/manga/one-piece/capitulo-", 567
        Output: "https://site.com/manga/one-piece/capitulo-567/"
        
        Input: "https://site.com/manga/naruto/", 10
        Output: "https://site.com/manga/naruto/capitulo-10/"
    """
    import re
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    # Caso 1: URL já termina com "capitulo-" (padrão mais comum)
    if base_url.endswith('capitulo-') or base_url.endswith('capitulo_'):
        # Remove o último caractere (-) e adiciona número
        base_url = base_url.rstrip('-_')
        return f"{base_url}-{numero_capitulo}/"
    
    # Caso 2: URL já termina com "chap-" ou "chapter-"
    if base_url.endswith('chap-') or base_url.endswith('chapter-'):
        base_url = base_url.rstrip('-_')
        return f"{base_url}-{numero_capitulo}/"
    
    # Caso 3: URL já tem um número no final (substitui)
    # Ex: "site.com/manga/naruto/capitulo-566" -> "site.com/manga/naruto/capitulo-567"
    if re.search(r'capitulo[-_]?\d+$', base_url, re.IGNORECASE):
        base_url = re.sub(r'(capitulo[-_]?)\d+$', r'\g<1>', base_url, flags=re.IGNORECASE)
        return f"{base_url}{numero_capitulo}/"
    
    # Caso 4: URL termina só com o nome do mangá (adiciona /capitulo-)
    # Ex: "site.com/manga/one-piece" -> "site.com/manga/one-piece/capitulo-567/"
    return f"{base_url}/capitulo-{numero_capitulo}/"


@api_bp.route('/manga/<nome_manga>/chapters', methods=['GET'])
def get_chapters(nome_manga):
    """Lista capítulos de um mangá (JSON)"""
    container = current_app.container
    
    manga = container.manga_repository.buscar_por_nome(nome_manga)
    if not manga:
        return jsonify({'error': 'Mangá não encontrado'}), 404
    
    ordem = request.args.get('ordem', 'asc')
    capitulos = container.capitulo_repository.listar_por_manga(nome_manga, ordem=ordem)
    
    resultado = []
    for cap in capitulos:
        resultado.append({
            'filename': cap.nome_arquivo,
            'title': cap.nome_arquivo.replace('.pdf', ''),
            'url': url_for('capitulo.visualizar_pdf', nome_manga=nome_manga, nome_arquivo=cap.nome_arquivo, _external=True),
            'thumbnail': url_for('capitulo.visualizar_thumbnail', nome_manga=nome_manga, nome_arquivo=cap.nome_arquivo, _external=True) if cap.tem_thumbnail else None,
            'read': False  # TODO: Implementar leitura
        })
    
    return jsonify(resultado)

@api_bp.route('/library/<nome_manga>', methods=['GET'])
def get_manga_chapters(nome_manga):
    """
    Lista capítulos de um mangá específico (JSON para React)
    
    Params:
        nome_manga: Nome do mangá (URL encoded)
        ordem: Query param 'asc' ou 'desc' (default: 'asc')
    """
    try:
        container = current_app.container
        
        # Decodifica nome do mangá
        from urllib.parse import unquote
        nome_decodificado = unquote(nome_manga)
        
        # Verifica se mangá existe
        manga = container.manga_repository.buscar_por_nome(nome_decodificado)
        if not manga:
            return jsonify({
                'error': 'Mangá não encontrado',
                'manga': nome_decodificado
            }), 404
        
        # Pega ordem (asc ou desc)
        ordem = request.args.get('ordem', 'asc')
        
        # Lista capítulos
        capitulos = container.capitulo_repository.listar_por_manga(nome_decodificado, ordem=ordem)
        
        # Prepara resposta
        chapters = []
        for cap in capitulos:
            chapters.append({
                'filename': cap.nome_arquivo,
                'title': cap.nome_arquivo.replace('.pdf', '').replace('_', ' '),
                'url': url_for(
                    'capitulo.visualizar_pdf', 
                    nome_manga=nome_decodificado, 
                    nome_arquivo=cap.nome_arquivo, 
                    _external=True
                ),
                'thumbnail': url_for(
                    'capitulo.visualizar_thumbnail',
                    nome_manga=nome_decodificado,
                    nome_arquivo=cap.nome_arquivo,
                    _external=True
                ) if cap.thumbnail_url else None,
                'read': False  # TODO: Implementar sistema de leitura
            })
        
        return jsonify({
            'manga': nome_decodificado,
            'total': len(chapters),
            'chapters': chapters
        })
        
    except Exception as e:
        current_app.logger.exception(f"Erro ao listar capítulos: {e}")
        return jsonify({
            'error': 'Erro interno ao buscar capítulos',
            'details': str(e)
        }), 500