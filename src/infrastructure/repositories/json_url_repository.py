"""
JSON URL Repository - Implementação de repositório de URLs usando JSON
"""
from typing import List, Optional

from ...domain.entities import URLSalva
from ...domain.repositories import IURLSalvaRepository
from ..services import URLStorageService


class JSONURLRepository(IURLSalvaRepository):
    """
    Repositório de URLs salvas usando arquivo JSON.
    
    Usa URLStorageService internamente para persistência.
    """
    
    def __init__(self, storage_service: URLStorageService):
        """
        Args:
            storage_service: Serviço de armazenamento de URLs
        """
        self.storage = storage_service
    
    def listar_todas(self) -> List[URLSalva]:
        """Lista todas as URLs salvas ativas"""
        urls_dict = self.storage.carregar_urls()
        
        urls_salvas = []
        for nome_manga, url_base in urls_dict.items():
            try:
                # Detecta padrão de capítulo
                padrao = self._detectar_padrao(url_base)
                
                url_salva = URLSalva(
                    nome_manga=nome_manga,
                    url_base=url_base,
                    padrao_capitulo=padrao,
                    ativa=True
                )
                urls_salvas.append(url_salva)
                
            except ValueError:
                # URL inválida, pula
                continue
        
        return sorted(urls_salvas, key=lambda u: u.nome_manga.lower())
    
    def buscar_por_nome(self, nome_manga: str) -> Optional[URLSalva]:
        """Busca URL por nome do mangá"""
        url_base = self.storage.buscar_url(nome_manga)
        
        if not url_base:
            return None
        
        try:
            padrao = self._detectar_padrao(url_base)
            
            return URLSalva(
                nome_manga=nome_manga,
                url_base=url_base,
                padrao_capitulo=padrao,
                ativa=True
            )
        except ValueError:
            return None
    
    def salvar(self, url: URLSalva) -> URLSalva:
        """Salva ou atualiza uma URL"""
        sucesso = self.storage.adicionar_url(url.nome_manga, url.url_base)
        
        if not sucesso:
            raise Exception(f"Erro ao salvar URL para {url.nome_manga}")
        
        return url
    
    def deletar(self, nome_manga: str) -> bool:
        """Deleta uma URL salva"""
        return self.storage.remover_url(nome_manga)
    
    def existe(self, nome_manga: str) -> bool:
        """Verifica se URL existe"""
        return self.storage.url_existe(nome_manga)
    
    def _detectar_padrao(self, url_base: str) -> str:
        """
        Detecta padrão de capítulo na URL.
        """
        url_lower = url_base.lower()
        
        if 'capitulo-' in url_lower:
            return 'capitulo-'
        elif 'chap-' in url_lower:
            return 'chap-'
        elif 'chapter-' in url_lower:
            return 'chapter-'
        else:
            return 'capitulo-'  # Default