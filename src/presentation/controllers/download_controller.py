"""
Download Controller - Controller para download de capítulos
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from src.application.use_cases import BaixarCapituloDTO
import re

download_bp = Blueprint('download', __name__)


@download_bp.route('/', methods=['GET', 'POST'])
def index():
    """Página inicial com formulário de download"""
    
    if request.method == 'GET':
        # Carrega URLs salvas para exibir
        container = current_app.container
        urls_salvas_entities = container.url_repository.listar_todas()
        
        # Converte para dicionário simples para o template
        urls_salvas = {url.nome_manga: url.url_base for url in urls_salvas_entities}
        
        return render_template('index.html', urls_salvas=urls_salvas)
    
    # POST - Processar download
    acao = request.form.get('acao')
    container = current_app.container
    
    # Ação: Salvar URL
    if acao == 'salvar_url':
        nova_url = request.form.get('nova_url', '').strip()
        nome_manga = request.form.get('nome_manga', '').strip()
        
        if nova_url and nome_manga:
            try:
                from src.domain.entities import URLSalva
                url_salva = URLSalva(
                    nome_manga=nome_manga,
                    url_base=nova_url
                )
                container.url_repository.salvar(url_salva)
                flash(f"URL para '{nome_manga}' salva com sucesso!", 'success')
            except Exception as e:
                flash(f"Erro ao salvar URL: {str(e)}", 'error')
        else:
            flash('Nome do mangá e URL são obrigatórios para salvar.', 'error')
        
        return redirect(url_for('download.index'))
    
    # Ação: Remover URL
    elif acao == 'remover_url':
        nome_manga = request.form.get('nome_manga', '').strip()
        
        if container.url_repository.deletar(nome_manga):
            flash(f"URL de '{nome_manga}' removida com sucesso!", 'success')
        else:
            flash(f"URL para '{nome_manga}' não encontrada.", 'error')
        
        return redirect(url_for('download.index'))
    
    # Ação: Baixar capítulo
    elif acao in ('baixar_manual', 'baixar_predefinida'):
        base_url = request.form.get('base_url', '').strip()
        capitulo_str = request.form.get('capitulo', '').strip()
        nome_manga_form = request.form.get('nome_manga', '').strip()
        
        # Validações básicas
        if not base_url or not capitulo_str:
            flash('URL e número do capítulo são obrigatórios.', 'error')
            return redirect(url_for('download.index'))
        
        if not capitulo_str.isdigit():
            flash('Número do capítulo deve ser um número válido.', 'error')
            return redirect(url_for('download.index'))
        
        numero_capitulo = int(capitulo_str)
        
        # Extrai nome do mangá da URL se não fornecido
        if not nome_manga_form:
            nome_manga_form = _extrair_nome_manga_da_url(base_url)
        
        # Limpa sufixos como "-manga-pt-br"
        nome_manga_limpo = _limpar_sufixo_manga(nome_manga_form)
        
        # Constrói URL completa do capítulo
        url_capitulo = _construir_url_capitulo(base_url, numero_capitulo)
        
        # Cria DTO
        dto = BaixarCapituloDTO(
            url_capitulo=url_capitulo,
            nome_manga=nome_manga_limpo,
            numero_capitulo=numero_capitulo,
            sobrescrever=False
        )
        
        # Executa use case
        resultado = container.baixar_capitulo_use_case.executar(dto)
        
        if resultado.sucesso:
            flash(resultado.mensagem, 'success')
        else:
            flash(resultado.mensagem, 'error')
        
        return redirect(url_for('download.index'))
    
    return redirect(url_for('download.index'))


def _extrair_nome_manga_da_url(url: str) -> str:
    """Extrai nome do mangá da URL"""
    from urllib.parse import urlparse
    
    partes = urlparse(url).path.strip('/').split('/')
    for parte in reversed(partes):
        if parte and 'capitulo' not in parte.lower() and 'chap' not in parte.lower():
            return parte.replace('-', ' ').replace('_', ' ').title()
    
    return 'Manga_Desconhecido'


def _limpar_sufixo_manga(nome: str) -> str:
    """Remove sufixos como '-manga-pt-br'"""
    padrao = r'[-_\s]*(manga[-_\s]*)?pt[-_\s]*br$'
    return re.sub(padrao, '', nome, flags=re.IGNORECASE).strip()


def _construir_url_capitulo(base_url: str, numero: int) -> str:
    """Constrói URL completa do capítulo"""
    # Detecta se precisa sufixo -pt-br
    sufixo = '-pt-br' if 'manga-pt-br' in base_url.lower() else ''
    
    # Se URL já termina com número, substitui
    if base_url[-1].isdigit():
        # Remove último número
        base_url = re.sub(r'\d+/?$', '', base_url)
    
    # Garante que termina com padrão correto
    if not base_url.endswith(('capitulo-', 'chap-', 'chapter-')):
        if 'capitulo' in base_url.lower():
            base_url = base_url.rstrip('/') + '/'
    
    return f"{base_url}{numero}{sufixo}/"