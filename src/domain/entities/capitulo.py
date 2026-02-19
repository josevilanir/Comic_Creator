"""
Entidade Capitulo - Representa um capítulo de mangá
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Capitulo:
    """
    Representa um capítulo individual de um mangá.
    
    Regras de negócio:
    - Número do capítulo deve ser positivo
    - Nome do arquivo deve ter extensão .pdf
    - Um capítulo pertence a um mangá
    """
    numero: int
    nome_arquivo: str
    manga_nome: str
    caminho_completo: str
    thumbnail_url: Optional[str] = None
    lido: bool = False
    data_download: Optional[datetime] = None
    tamanho_bytes: Optional[int] = None
    
    def __post_init__(self):
        """Validações da entidade capítulo"""
        if self.numero < 0:
            raise ValueError("Número do capítulo deve ser positivo")
        
        if not self.nome_arquivo.endswith('.pdf'):
            raise ValueError("Nome do arquivo deve ter extensão .pdf")
        
        if not self.manga_nome or not self.manga_nome.strip():
            raise ValueError("Capítulo deve pertencer a um mangá")
    
    def marcar_como_lido(self):
        """Marca o capítulo como lido"""
        self.lido = True
    
    def marcar_como_nao_lido(self):
        """Desmarca o capítulo como lido"""
        self.lido = False
    
    def tem_thumbnail(self) -> bool:
        """Verifica se o capítulo possui thumbnail"""
        return self.thumbnail_url is not None
    
    @property
    def nome_exibicao(self) -> str:
        """Retorna nome formatado para exibição"""
        return self.nome_arquivo.replace('.pdf', '')