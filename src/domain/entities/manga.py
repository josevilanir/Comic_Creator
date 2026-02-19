"""
Entidade Manga - Representa um mangá no domínio do sistema
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Manga:
    """
    Entidade principal que representa um mangá na biblioteca.
    
    Regras de negócio:
    - Nome deve ser único e não vazio
    - Caminho deve apontar para diretório válido
    """
    nome: str
    caminho: str
    capa_url: Optional[str] = None
    tem_capa: bool = False
    data_criacao: Optional[datetime] = None
    total_capitulos: int = 0
    
    def __post_init__(self):
        """Validações básicas da entidade"""
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do mangá não pode ser vazio")
        
        if not self.caminho or not self.caminho.strip():
            raise ValueError("Caminho do mangá não pode ser vazio")
        
        # Normaliza o nome
        self.nome = self.nome.strip()
    
    def adicionar_capitulo(self):
        """Incrementa contador de capítulos"""
        self.total_capitulos += 1
    
    def remover_capitulo(self):
        """Decrementa contador de capítulos"""
        if self.total_capitulos > 0:
            self.total_capitulos -= 1
    
    def atualizar_capa(self, capa_url: str):
        """Atualiza informações da capa"""
        self.capa_url = capa_url
        self.tem_capa = True