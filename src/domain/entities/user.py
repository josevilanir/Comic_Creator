"""
Entidade User - Representa um usuário do sistema
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """
    Representa um usuário do sistema.
    
    Regras de negócio:
    - Username deve ser único
    - Username deve ter entre 3 e 50 caracteres
    - Senha deve ser armazenada com hash
    """
    id: Optional[int]
    username: str
    password_hash: str
    data_criacao: Optional[datetime] = None
    ultimo_acesso: Optional[datetime] = None
    
    def __post_init__(self):
        """Validações da entidade usuário"""
        if not self.username or not self.username.strip():
            raise ValueError("Username não pode ser vazio")
        
        username_limpo = self.username.strip()
        
        if len(username_limpo) < 3:
            raise ValueError("Username deve ter no mínimo 3 caracteres")
        
        if len(username_limpo) > 50:
            raise ValueError("Username deve ter no máximo 50 caracteres")
        
        self.username = username_limpo
    
    def atualizar_ultimo_acesso(self):
        """Atualiza timestamp do último acesso"""
        self.ultimo_acesso = datetime.now()
    
    @property
    def esta_ativo(self) -> bool:
        """Verifica se o usuário tem acesso recente"""
        if not self.ultimo_acesso:
            return False
        
        dias_inativo = (datetime.now() - self.ultimo_acesso).days
        return dias_inativo < 90  # 90 dias de inatividade