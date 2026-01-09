"""
Entidade URLSalva - Representa uma URL predefinida de mangá
"""
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class URLSalva:
    """
    Representa uma URL salva para download rápido de mangás.
    
    Regras de negócio:
    - Nome deve ser único
    - URL deve ser válida
    - URL deve terminar com padrão de capítulo (capitulo-, chap-, etc)
    """
    nome_manga: str
    url_base: str
    padrao_capitulo: str = "capitulo-"  # capitulo-, chap-, etc
    ativa: bool = True
    
    def __post_init__(self):
        """Validações da entidade URL Salva"""
        if not self.nome_manga or not self.nome_manga.strip():
            raise ValueError("Nome do mangá não pode ser vazio")
        
        if not self.url_base or not self.url_base.strip():
            raise ValueError("URL base não pode ser vazia")
        
        # Valida se é uma URL
        try:
            resultado = urlparse(self.url_base)
            if not all([resultado.scheme, resultado.netloc]):
                raise ValueError("URL inválida")
        except Exception:
            raise ValueError("URL mal formatada")
        
        self.nome_manga = self.nome_manga.strip()
        self.url_base = self.url_base.strip()
    
    def construir_url_capitulo(self, numero_capitulo: int, sufixo: str = "") -> str:
        """
        Constrói a URL completa para um capítulo específico
        
        Args:
            numero_capitulo: Número do capítulo
            sufixo: Sufixo adicional (ex: -pt-br)
        
        Returns:
            URL completa do capítulo
        """
        if numero_capitulo < 0:
            raise ValueError("Número do capítulo deve ser positivo")
        
        return f"{self.url_base}{numero_capitulo}{sufixo}/"
    
    def desativar(self):
        """Desativa a URL (marca como inativa ao invés de deletar)"""
        self.ativa = False
    
    def ativar(self):
        """Reativa a URL"""
        self.ativa = True
    
    def detectar_sufixo_ptbr(self) -> bool:
        """Detecta se a URL requer sufixo -pt-br"""
        return 'manga-pt-br' in self.url_base.lower() or 'pt-br' in self.nome_manga.lower()