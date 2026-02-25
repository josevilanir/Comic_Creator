"""
API REST Routes - Endpoints JSON para o frontend React
"""
from flask import Blueprint, request, current_app, url_for, g
import threading
import uuid

from src.presentation.api.jsend import success, error, fail
from src.presentation.decorators.auth_required import auth_required

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/library', methods=['GET'])
@auth_required
def get_library():
    """Lista todos os mangás do usuário logado"""
    container = current_app.container
    mangas = container.manga_repository.listar_todos(g.user_id)
    
    resultado = []
    for manga in mangas:
        resultado.append({
            'nome': manga.nome,
            'tem_capa': manga.tem_capa,
            'capa_url': url_for('manga.visualizar_capa', nome_manga=manga.nome, _external=True) if manga.tem_capa else None,
            'total_capitulos': manga.total_capitulos
        })
    
    return success(resultado)


@api_bp.route('/urls', methods=['GET'])
@auth_required
def get_urls():
    """Lista URLs salvas do usuário"""
    container = current_app.container
    urls_entities = container.url_repository.listar_todas(g.user_id)
    urls_dict = {url.nome_manga: url.url_base for url in urls_entities}
    return success(urls_dict)


@api_bp.route('/urls', methods=['POST'])
@auth_required
def save_url():
    """Salva nova URL para o usuário"""
    data = request.json or {}
    nome = data.get('nome')
    url = data.get('url')
    
    if not nome or not url:
        return fail({'nome': 'obrigatório', 'url': 'obrigatório'})
    
    try:
        from src.domain.entities import URLSalva
        container = current_app.container
        url_salva = URLSalva(nome_manga=nome, url_base=url)
        container.url_repository.salvar(g.user_id, url_salva)
        return success({'message': 'URL salva com sucesso!'}, 201)
    except Exception as e:
        return error(str(e), 'SAVE_URL_ERROR')


@api_bp.route('/urls', methods=['DELETE'])
@auth_required
def delete_url():
    """Remove URL salva do usuário"""
    data = request.json or {}
    nome = data.get('nome')
    if not nome:
        return fail({'nome': 'obrigatório'})
    
    try:
        container = current_app.container
        if container.url_repository.deletar(g.user_id, nome):
            return success({'message': 'URL removida!'})
        return fail({'nome': 'URL não encontrada'}, 404)
    except Exception as e:
        return error(str(e), 'DELETE_URL_ERROR')

@api_bp.route('/download', methods=['POST'])
@auth_required
def download_chapter():
    """Baixa capítulo para o usuário logado"""
    data = request.json or {}
    base_url = data.get('base_url')
    capitulo = data.get('capitulo')
    nome_manga = data.get('nome_manga')
    
    if not all([base_url, capitulo, nome_manga]):
        return fail({'base_url': 'obrigat.', 'capitulo': 'obrigat.', 'nome_manga': 'obrigat.'})
    
    try:
        container = current_app.container
        from src.application.use_cases import BaixarCapituloDTO
        import re
        
        def limpar_sufixo(nome: str) -> str:
            padrao = r'[-_\s]*(manga[-_\s]*)?pt[-_\s]*br$'
            return re.sub(padrao, '', nome, flags=re.IGNORECASE).strip()
        
        nome_limpo = limpar_sufixo(nome_manga)
        url_completa = construir_url_capitulo_correta(base_url, int(capitulo))
        
        # TODO: BaixarCapituloUseCase deve ser atualizado para aceitar user_id
        # Para este MVP, vamos forçar o salvamento na pasta do usuário via repo
        dto = BaixarCapituloDTO(
            url_capitulo=url_completa,
            nome_manga=nome_limpo,
            numero_capitulo=int(capitulo),
            sobrescrever=False
        )
        
        # Atualizamos o use case para receber user_id no executar ou no construtor.
        # Vamos assumir que atualizaremos o executar.
        resultado = container.baixar_capitulo_use_case.executar(dto, user_id=g.user_id)
        
        if resultado.sucesso:
            return success({'message': resultado.mensagem})
        return fail({'download': resultado.mensagem})
    except Exception as e:
        return error(str(e), 'DOWNLOAD_ERROR')

_download_jobs: dict = {}
_jobs_lock = threading.Lock()

@api_bp.route('/download/range', methods=['POST'])
@auth_required
def download_range():
    data = request.json or {}
    base_url   = data.get('base_url', '').strip()
    cap_inicio = data.get('cap_inicio')
    cap_fim    = data.get('cap_fim')
    nome_manga = data.get('nome_manga', '').strip() or 'Manga'

    if not base_url or cap_inicio is None or cap_fim is None:
        return fail({'message': 'Dados incompletos'})

    cap_inicio, cap_fim = int(cap_inicio), int(cap_fim)
    total = cap_fim - cap_inicio + 1
    
    job_id = str(uuid.uuid4())[:8]
    with _jobs_lock:
        _download_jobs[job_id] = {
            'status': 'rodando', 'total': total, 'concluido': 0, 'atual': None, 
            'resultados': [], 'cancelar': False, 'user_id': g.user_id
        }

    app = current_app._get_current_object()
    threading.Thread(
        target=_executar_range_download,
        args=(app, job_id, base_url, cap_inicio, cap_fim, nome_manga, g.user_id),
        daemon=True,
    ).start()

    return success({'job_id': job_id, 'total': total}, 202)

@api_bp.route('/download/progresso/<job_id>', methods=['GET'])
@auth_required
def download_progresso(job_id):
    with _jobs_lock:
        job = _download_jobs.get(job_id)
    if not job or job.get('user_id') != g.user_id:
        return fail({'job_id': 'Job não encontrado ou acesso negado'}, 404)
    return success(job)

@api_bp.route('/download/cancelar/<job_id>', methods=['POST'])
@auth_required
def download_cancelar(job_id):
    with _jobs_lock:
        job = _download_jobs.get(job_id)
        if not job or job.get('user_id') != g.user_id:
            return fail({'job_id': 'Job não encontrado'}, 404)
        job['cancelar'] = True
    return success({'message': 'Cancelamento solicitado'})

def _executar_range_download(app, job_id, base_url, cap_inicio, cap_fim, nome_manga, user_id):
    import re
    def limpar_sufixo(nome: str) -> str:
        padrao = r'[-_\s]*(manga[-_\s]*)?pt[-_\s]*br$'
        return re.sub(padrao, '', nome, flags=re.IGNORECASE).strip()
    nome_limpo = limpar_sufixo(nome_manga)

    with app.app_context():
        from src.application.use_cases import BaixarCapituloDTO
        container = app.container
        for cap_num in range(cap_inicio, cap_fim + 1):
            with _jobs_lock:
                job = _download_jobs[job_id]
                if job['cancelar']: 
                    job['status'] = 'cancelado'
                    break
                job['atual'] = cap_num

            try:
                url_completa = construir_url_capitulo_correta(base_url, cap_num)
                dto = BaixarCapituloDTO(url_completa, nome_limpo, cap_num, False)
                resultado = container.baixar_capitulo_use_case.executar(dto, user_id=user_id)
                with _jobs_lock:
                    _download_jobs[job_id]['resultados'].append({
                        'cap': cap_num, 'sucesso': resultado.sucesso, 'mensagem': resultado.mensagem
                    })
                    _download_jobs[job_id]['concluido'] += 1
            except Exception as e:
                with _jobs_lock:
                    _download_jobs[job_id]['resultados'].append({
                        'cap': cap_num, 'sucesso': False, 'mensagem': str(e)
                    })
                    _download_jobs[job_id]['concluido'] += 1

        with _jobs_lock:
            if _download_jobs[job_id]['status'] == 'rodando':
                _download_jobs[job_id]['status'] = 'concluido'
                _download_jobs[job_id]['atual'] = None

@api_bp.route('/library/<nome_manga>', methods=['DELETE'])
@auth_required
def delete_manga(nome_manga):
    from urllib.parse import unquote
    nome_decodificado = unquote(nome_manga)
    try:
        container = current_app.container
        if not container.manga_repository.existe(g.user_id, nome_decodificado):
            return fail({'nome_manga': 'Mangá não encontrado.'}, 404)
        if container.manga_repository.deletar(g.user_id, nome_decodificado):
            try: container.url_repository.deletar(g.user_id, nome_decodificado)
            except: pass
            return success({'message': f"Mangá '{nome_decodificado}' excluído."})
        return error('Erro ao excluir mangá.', 'DELETE_MANGA_ERROR')
    except Exception as e:
        return error(str(e), 'DELETE_MANGA_ERROR')

@api_bp.route('/library/<nome_manga>/<nome_arquivo>', methods=['DELETE'])
@auth_required
def delete_capitulo(nome_manga, nome_arquivo):
    from urllib.parse import unquote
    nome_decodificado, arquivo_decodificado = unquote(nome_manga), unquote(nome_arquivo)
    if '..' in nome_decodificado or '..' in arquivo_decodificado:
        return fail({'error': 'Acesso negado.'}, 403)
    try:
        container = current_app.container
        if container.capitulo_repository.deletar(g.user_id, nome_decodificado, arquivo_decodificado):
            return success({'message': f"Capítulo '{arquivo_decodificado}' excluído."})
        return fail({'nome_arquivo': 'Não encontrado.'}, 404)
    except Exception as e:
        return error(str(e), 'DELETE_CAPITULO_ERROR')

@api_bp.route('/library/<nome_manga>/capa', methods=['POST'])
@auth_required
def upload_capa(nome_manga):
    from urllib.parse import unquote
    from PIL import Image
    import os
    nome_decodificado = unquote(nome_manga)
    try:
        container = current_app.container
        manga = container.manga_repository.buscar_por_nome(g.user_id, nome_decodificado)
        if not manga: return fail({'nome_manga': 'Não encontrado.'}, 404)
        if 'capa' not in request.files: return fail({'capa': 'Nenhum arquivo enviado.'})
        file = request.files['capa']
        img = Image.open(file.stream).convert('RGB')
        img.save(os.path.join(manga.caminho, 'capa.jpg'), 'JPEG', quality=90)
        nova_url = url_for('manga.visualizar_capa', nome_manga=nome_decodificado, _external=True)
        return success({'message': 'Capa atualizada!', 'capa_url': nova_url})
    except Exception as e:
        return error(str(e), 'UPLOAD_CAPA_ERROR')

def construir_url_capitulo_correta(base_url: str, numero_capitulo: int) -> str:
    import re
    base_url = base_url.rstrip('/')
    match = re.search(r'(capitulo[-_]?|chap[-_]?|chapter[-_]?)(\d+)$', base_url, re.IGNORECASE)
    if match:
        prefixo, num_exemplo = match.group(1), match.group(2)
        largura = len(num_exemplo)
        base_sem_num = base_url[:match.start()] + prefixo
        num_formatado = str(numero_capitulo).zfill(largura) if num_exemplo.startswith('0') and largura > 1 else str(numero_capitulo)
        return f"{base_sem_num}{num_formatado}/"
    if re.search(r'(capitulo[-_]|chap[-_]|chapter[-_])$', base_url, re.IGNORECASE):
        return f"{base_url}{numero_capitulo}/"
    return f"{base_url}/capitulo-{numero_capitulo}/"

@api_bp.route('/library/<nome_manga>', methods=['GET'])
@auth_required
def get_manga_chapters(nome_manga):
    from urllib.parse import unquote
    nome_decodificado = unquote(nome_manga)
    try:
        container = current_app.container
        manga = container.manga_repository.buscar_por_nome(g.user_id, nome_decodificado)
        if not manga: return fail({'error': 'Mangá não encontrado'}, 404)
        ordem = request.args.get('ordem', 'asc')
        capitulos = container.capitulo_repository.listar_por_manga(g.user_id, nome_decodificado, ordem=ordem)
        lidos = container.user_data_repository.get_reads(g.user_id, nome_decodificado)
        chapters = [{
            'filename': cap.nome_arquivo, 'title': cap.nome_arquivo.replace('.pdf', '').replace('_', ' '),
            'url': url_for('capitulo.visualizar_pdf', nome_manga=nome_decodificado, nome_arquivo=cap.nome_arquivo, _external=True),
            'thumbnail': url_for('capitulo.visualizar_thumbnail', nome_manga=nome_decodificado, nome_arquivo=cap.nome_arquivo, _external=True) if cap.tem_thumbnail else None,
            'read': cap.nome_arquivo in lidos
        } for cap in capitulos]
        return success({'manga': nome_decodificado, 'total': len(chapters), 'chapters': chapters})
    except Exception as e:
        return error(str(e), 'GET_CHAPTERS_ERROR')
