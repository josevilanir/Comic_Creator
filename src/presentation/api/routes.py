"""
API REST Routes - Endpoints JSON para o frontend React
"""
from flask import Blueprint, request, current_app, url_for
import threading
import uuid

from src.presentation.api.jsend import success, error, fail

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


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
    
    return success(resultado)


@api_bp.route('/urls', methods=['GET'])
def get_urls():
    """Lista URLs salvas (JSON)"""
    container = current_app.container
    urls_entities = container.url_repository.listar_todas()
    
    # Converte para dicionário {nome: url}
    urls_dict = {url.nome_manga: url.url_base for url in urls_entities}
    
    return success(urls_dict)


@api_bp.route('/urls', methods=['POST'])
def save_url():
    """Salva nova URL"""
    data = request.json or {}
    nome = data.get('nome')
    url = data.get('url')
    
    if not nome or not url:
        return fail({'nome': 'obrigatório', 'url': 'obrigatório'})
    
    try:
        from src.domain.entities import URLSalva
        container = current_app.container
        
        url_salva = URLSalva(nome_manga=nome, url_base=url)
        container.url_repository.salvar(url_salva)
        
        return success({'message': 'URL salva com sucesso!'}, 201)
    except Exception as e:
        return error(str(e), 'SAVE_URL_ERROR')


@api_bp.route('/urls', methods=['DELETE'])
def delete_url():
    """Remove URL salva"""
    data = request.json or {}
    nome = data.get('nome')
    
    if not nome:
        return fail({'nome': 'obrigatório'})
    
    try:
        container = current_app.container
        sucesso = container.url_repository.deletar(nome)
        
        if sucesso:
            return success({'message': 'URL removida!'})
        else:
            return fail({'nome': 'URL não encontrada'}, 404)
    except Exception as e:
        return error(str(e), 'DELETE_URL_ERROR')

@api_bp.route('/download', methods=['POST'])
def download_chapter():
    """Baixa capítulo"""
    data = request.json or {}
    base_url = data.get('base_url')
    capitulo = data.get('capitulo')
    nome_manga = data.get('nome_manga')
    
    if not all([base_url, capitulo, nome_manga]):
        return fail({
            'base_url': 'obrigatório',
            'capitulo': 'obrigatório',
            'nome_manga': 'obrigatório'
        })
    
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
            return success({'message': resultado.mensagem})
        else:
            return fail({'download': resultado.mensagem})
            
    except Exception as e:
        current_app.logger.exception(f"Erro no download: {e}")
        return error(str(e), 'DOWNLOAD_ERROR')

_download_jobs: dict = {}
_jobs_lock = threading.Lock()

# ─── Endpoint: iniciar range download ─────────────────────────────────────────
@api_bp.route('/download/range', methods=['POST'])
def download_range():
    """
    Inicia download de um range de capítulos em thread separada.

    Body JSON:
        base_url   (str)  — URL base do mangá
        cap_inicio (int)  — capítulo inicial (inclusivo)
        cap_fim    (int)  — capítulo final (inclusivo)
        nome_manga (str)  — nome do mangá

    Retorna:
        { job_id, total } — ID para consultar progresso via GET /api/download/progresso/<job_id>
    """
    data = request.json or {}
    base_url   = data.get('base_url', '').strip()
    cap_inicio = data.get('cap_inicio')
    cap_fim    = data.get('cap_fim')
    nome_manga = data.get('nome_manga', '').strip() or 'Manga'

    # Validações
    if not base_url:
        return fail({'base_url': 'obrigatório'})
    if cap_inicio is None or cap_fim is None:
        return fail({'cap_inicio': 'obrigatório', 'cap_fim': 'obrigatório'})

    cap_inicio = int(cap_inicio)
    cap_fim    = int(cap_fim)

    if cap_inicio < 1 or cap_fim < cap_inicio:
        return fail({'range': 'cap_inicio deve ser ≥ 1 e ≤ cap_fim'})

    total = cap_fim - cap_inicio + 1
    if total > 200:
        return fail({'range': 'Máximo de 200 capítulos por download'})

    # Cria job
    job_id = str(uuid.uuid4())[:8]
    with _jobs_lock:
        _download_jobs[job_id] = {
            'status':    'rodando',   # rodando | concluido | cancelado
            'total':     total,
            'concluido': 0,
            'atual':     None,        # capítulo sendo baixado agora
            'resultados': [],         # lista de { cap, sucesso, mensagem }
            'cancelar':  False,       # flag para cancelamento
        }

    # Dispara thread de download
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=_executar_range_download,
        args=(app, job_id, base_url, cap_inicio, cap_fim, nome_manga),
        daemon=True,
    )
    thread.start()

    return success({'job_id': job_id, 'total': total}, 202)


# ─── Endpoint: consultar progresso ────────────────────────────────────────────
@api_bp.route('/download/progresso/<job_id>', methods=['GET'])
def download_progresso(job_id):
    """
    Retorna o progresso atual de um job de range download.

    Retorna:
        {
          status:    'rodando' | 'concluido' | 'cancelado',
          total:     int,
          concluido: int,
          atual:     int | null,
          resultados: [{ cap, sucesso, mensagem }]
        }
    """
    with _jobs_lock:
        job = _download_jobs.get(job_id)

    if not job:
        return fail({'job_id': 'Job não encontrado'}, 404)

    return success(job)


# ─── Endpoint: cancelar job ────────────────────────────────────────────────────
@api_bp.route('/download/cancelar/<job_id>', methods=['POST'])
def download_cancelar(job_id):
    """Sinaliza cancelamento de um job em andamento."""
    with _jobs_lock:
        job = _download_jobs.get(job_id)
        if not job:
            return fail({'job_id': 'Job não encontrado'}, 404)
        job['cancelar'] = True

    return success({'message': 'Cancelamento solicitado'})


# ─── Worker: executa o range em background ────────────────────────────────────
def _executar_range_download(app, job_id: str, base_url: str, cap_inicio: int, cap_fim: int, nome_manga: str):
    """
    Função executada em thread separada.
    Itera pelos capítulos do range e atualiza o estado do job a cada capítulo.
    """
    import re

    def limpar_sufixo(nome: str) -> str:
        padrao = r'[-_\s]*(manga[-_\s]*)?pt[-_\s]*br$'
        return re.sub(padrao, '', nome, flags=re.IGNORECASE).strip()

    nome_limpo = limpar_sufixo(nome_manga)

    with app.app_context():
        from src.application.use_cases import BaixarCapituloDTO
        container = app.container

        for cap_num in range(cap_inicio, cap_fim + 1):
            # Verifica cancelamento antes de cada capítulo
            with _jobs_lock:
                job = _download_jobs[job_id]
                if job['cancelar']:
                    job['status'] = 'cancelado'
                    break
                job['atual'] = cap_num

            try:
                url_completa = construir_url_capitulo_correta(base_url, cap_num)

                dto = BaixarCapituloDTO(
                    url_capitulo=url_completa,
                    nome_manga=nome_limpo,
                    numero_capitulo=cap_num,
                    sobrescrever=False,
                )

                resultado = container.baixar_capitulo_use_case.executar(dto)

                with _jobs_lock:
                    _download_jobs[job_id]['resultados'].append({
                        'cap':      cap_num,
                        'sucesso':  resultado.sucesso,
                        'mensagem': resultado.mensagem,
                    })
                    _download_jobs[job_id]['concluido'] += 1

            except Exception as e:
                with _jobs_lock:
                    _download_jobs[job_id]['resultados'].append({
                        'cap':      cap_num,
                        'sucesso':  False,
                        'mensagem': f'Erro inesperado: {str(e)}',
                    })
                    _download_jobs[job_id]['concluido'] += 1

        # Marca como concluído (se não foi cancelado)
        with _jobs_lock:
            job = _download_jobs[job_id]
            if job['status'] == 'rodando':
                job['status']  = 'concluido'
                job['atual']   = None

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
            return fail({'nome_manga': 'Mangá não encontrado.'}, 404)

        if container.manga_repository.deletar(nome_decodificado):
            # Remove URL salva associada, se existir
            try:
                container.url_repository.deletar(nome_decodificado)
            except Exception:
                pass  # URL pode não existir — não é erro crítico

            current_app.logger.info(f"Mangá deletado via API: {nome_decodificado}")
            return success({
                'message': f"Mangá '{nome_decodificado}' e todos os seus capítulos foram excluídos."
            })
        else:
            return error('Erro ao excluir mangá.', 'DELETE_MANGA_ERROR')

    except Exception as e:
        current_app.logger.exception(f"Erro ao deletar mangá '{nome_decodificado}': {e}")
        return error(str(e), 'DELETE_MANGA_ERROR')

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
        return fail({'error': 'Acesso negado.'}, 403)

    try:
        container = current_app.container

        # Verifica se o mangá existe antes de tentar deletar
        if not container.manga_repository.existe(nome_decodificado):
            return fail({'nome_manga': 'Mangá não encontrado.'}, 404)

        # Deleta via repositório (remove PDF + thumbnail automaticamente)
        if container.capitulo_repository.deletar(nome_decodificado, arquivo_decodificado):
            current_app.logger.info(
                f"Capítulo deletado via API: {nome_decodificado}/{arquivo_decodificado}"
            )
            return success({
                'message': f"Capítulo '{arquivo_decodificado.replace('.pdf', '')}' excluído com sucesso!"
            })
        else:
            return fail({
                'nome_arquivo': 'Capítulo não encontrado no disco.'
            }), 404

    except Exception as e:
        current_app.logger.exception(
            f"Erro ao deletar capítulo '{arquivo_decodificado}' de '{nome_decodificado}': {e}"
        )
        return error(str(e), 'DELETE_CAPITULO_ERROR')

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
            return fail({'nome_manga': 'Mangá não encontrado.'}, 404)

        if 'capa' not in request.files:
            return fail({'capa': 'Nenhum arquivo enviado.'})

        file = request.files['capa']

        if file.filename == '':
            return fail({'capa': 'Arquivo sem nome.'})

        extensoes_permitidas = {'png', 'jpg', 'jpeg', 'webp'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in extensoes_permitidas:
            return fail({
                'capa': 'Formato inválido. Use PNG, JPG, JPEG ou WEBP.'
            })

        # Converte para JPEG e salva como capa.jpg
        import os
        img = Image.open(file.stream).convert('RGB')
        caminho_capa = os.path.join(manga.caminho, 'capa.jpg')
        img.save(caminho_capa, 'JPEG', quality=90)

        current_app.logger.info(f"Capa atualizada via API: {nome_decodificado}")

        # Retorna a nova URL da capa para atualização imediata no frontend
        nova_url = url_for('manga.visualizar_capa', nome_manga=nome_decodificado, _external=True)
        return success({
            'message': f"Capa de '{nome_decodificado}' atualizada com sucesso!",
            'capa_url': nova_url
        })

    except Exception as e:
        current_app.logger.exception(f"Erro ao fazer upload de capa para '{nome_decodificado}': {e}")
        return error(str(e), 'UPLOAD_CAPA_ERROR')

def construir_url_capitulo_correta(base_url: str, numero_capitulo: int) -> str:
    """
    Constrói a URL correta do capítulo detectando e respeitando
    o zero-padding usado pelo site.

    Casos suportados:
      "site.com/capitulo-"    -> "site.com/capitulo-1/"    (sem padding)
      "site.com/capitulo-01"  -> "site.com/capitulo-01/"   (padding 2 dígitos)
      "site.com/capitulo-001" -> "site.com/capitulo-001/"  (padding 3 dígitos)
      "site.com/chap-02"      -> "site.com/chap-09/"       (padding detectado)
      "site.com/manga/titulo" -> "site.com/manga/titulo/capitulo-1/"
    """
    import re

    base_url = base_url.rstrip('/')

    # Caso 1: URL já termina com número embutido (ex: capitulo-01, chap-002)
    # Detecta o padrão e extrai o zero-padding do número de exemplo
    match = re.search(
        r'(capitulo[-_]?|chap[-_]?|chapter[-_]?)(\d+)$',
        base_url,
        re.IGNORECASE
    )
    if match:
        prefixo      = match.group(1)   # ex: "capitulo-"
        num_exemplo  = match.group(2)   # ex: "01"
        largura      = len(num_exemplo) # ex: 2

        # Reconstrói a base sem o número
        base_sem_num = base_url[:match.start()] + prefixo

        # Aplica padding somente se o exemplo original tinha zeros à esquerda
        if num_exemplo.startswith('0') and largura > 1:
            num_formatado = str(numero_capitulo).zfill(largura)
        else:
            # Número sem zero-padding (ex: "42") — usa puro
            num_formatado = str(numero_capitulo)

        return f"{base_sem_num}{num_formatado}/"

    # Caso 2: URL termina com separador sem número (ex: "capitulo-", "chap-")
    if re.search(r'(capitulo[-_]|chap[-_]|chapter[-_])$', base_url, re.IGNORECASE):
        return f"{base_url}{numero_capitulo}/"

    # Caso 3: URL sem padrão conhecido — adiciona /capitulo-N/
    return f"{base_url}/capitulo-{numero_capitulo}/"


@api_bp.route('/manga/<nome_manga>/chapters', methods=['GET'])
def get_chapters(nome_manga):
    """Lista capítulos de um mangá (JSON)"""
    container = current_app.container
    
    manga = container.manga_repository.buscar_por_nome(nome_manga)
    if not manga:
        return fail({'nome_manga': 'Mangá não encontrado'}, 404)
    
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
    
    return success(resultado)

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
            return fail({
                'error': 'Mangá não encontrado',
                'manga': nome_decodificado
            }, 404)
        
        # Pega ordem (asc ou desc)
        ordem = request.args.get('ordem', 'asc')
        
        # Lista capítulos
        capitulos = container.capitulo_repository.listar_por_manga(nome_decodificado, ordem=ordem)
        
        # Carrega estados de leitura
        from src.infrastructure.persistence.reads_repository import ReadsRepository
        from config.settings import Config
        reads_repo = ReadsRepository(str(Config.DATA_DIR / 'reads.json'))
        lidos = reads_repo.get_reads(nome_decodificado)

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
                'read': cap.nome_arquivo in lidos
            })
        
        return success({
            'manga': nome_decodificado,
            'total': len(chapters),
            'chapters': chapters
        })
        
    except Exception as e:
        current_app.logger.exception(f"Erro ao listar capítulos: {e}")
        return error('Erro interno ao buscar capítulos', 'GET_CHAPTERS_ERROR')
