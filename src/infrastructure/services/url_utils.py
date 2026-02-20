"""
Utilitários para manipulação de URLs
"""
import re


def limpar_sufixo_manga(nome: str) -> str:
    """Remove sufixos como '-manga-pt-br'"""
    padrao = r'[-_\s]*(manga[-_\s]*)?pt[-_\s]*br$'
    return re.sub(padrao, '', nome, flags=re.IGNORECASE).strip()


def construir_url_capitulo(base_url: str, numero: int) -> str:
    """Constrói URL completa do capítulo"""
    # Detecta se precisa sufixo -pt-br
    sufixo = '-pt-br' if 'manga-pt-br' in base_url.lower() else ''
    
    # Se URL já termina com número, substitui
    if base_url[-1].isdigit():
        base_url = re.sub(r'\d+/?$', '', base_url)
    
    # Garante padrão correto
    if not base_url.endswith('/'):
        base_url += '/'
    
    return f"{base_url}{numero}{sufixo}/"