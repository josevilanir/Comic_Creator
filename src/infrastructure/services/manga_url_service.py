"""
MangaUrlService — Serviço para adaptação de URLs e limpeza de nomes de mangás.
Implementa o Site-Adapter Pattern para lidar com diferentes estruturas de URL.
"""
import re
from abc import ABC, abstractmethod
from typing import List, Optional


class ISiteAdapter(ABC):
    """Interface para adaptadores de sites específicos."""
    
    @abstractmethod
    def matches(self, url: str) -> bool:
        """Verifica se este adaptador é capaz de lidar com a URL fornecida."""
        pass

    @abstractmethod
    def format_url(self, base_url: str, chapter_number: int) -> str:
        """Constrói a URL correta para o capítulo específico."""
        pass


class DefaultAdapter(ISiteAdapter):
    """Adaptador padrão baseado em heurísticas (regex)."""
    
    def matches(self, url: str) -> bool:
        return True  # Fallback para qualquer URL

    def format_url(self, base_url: str, chapter_number: int) -> str:
        base_url = base_url.rstrip('/')
        
        # Caso 1: URL já termina com número (ex: .../capitulo-1 ou .../chap-01)
        match = re.search(r'(capitulo[-_]?|chap[-_]?|chapter[-_]?)(\d+)$', base_url, re.IGNORECASE)
        if match:
            prefixo, num_exemplo = match.group(1), match.group(2)
            largura = len(num_exemplo)
            base_sem_num = base_url[:match.start()] + prefixo
            
            # Mantém padding de zeros se o exemplo tiver
            if num_exemplo.startswith('0') and largura > 1:
                num_formatado = str(chapter_number).zfill(largura)
            else:
                num_formatado = str(chapter_number)
                
            return f"{base_sem_num}{num_formatado}/"
            
        # Caso 2: Termina com prefixo mas sem número (ex: .../capitulo-)
        if re.search(r'(capitulo[-_]|chap[-_]|chapter[-_])$', base_url, re.IGNORECASE):
            return f"{base_url}{chapter_number}/"
            
        # Caso 3: URL base genérica (ex: .../manga/nome)
        # Adiciona o padrão mais comum
        return f"{base_url}/capitulo-{chapter_number}/"


class MangaUrlService:
    """Serviço que gerencia adaptadores de URL e utilitários de nome."""
    
    def __init__(self, adapters: Optional[List[ISiteAdapter]] = None):
        self.adapters = adapters or [DefaultAdapter()]

    def resolve_url(self, base_url: str, chapter_number: int) -> str:
        """Encontra o adaptador correto e formata a URL."""
        for adapter in self.adapters:
            if adapter.matches(base_url):
                return adapter.format_url(base_url, chapter_number)
        
        # Isso não deve ocorrer se o DefaultAdapter estiver na lista
        return DefaultAdapter().format_url(base_url, chapter_number)

    def clean_manga_name(self, name: str) -> str:
        """Remove sufixos comuns de sites e normaliza o nome."""
        # Padrao para remover: " - Manga", " pt-br", etc.
        patterns = [
            r'[-_\s]*(manga[-_\s]*)?pt[-_\s]*br$',
            r'[-_\s]+manga$',
        ]
        
        clean_name = name
        for p in patterns:
            clean_name = re.sub(p, '', clean_name, flags=re.IGNORECASE)
            
        return clean_name.strip()
