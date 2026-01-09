"""
Interfaces de Repositórios - Contratos para acesso a dados
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities import Manga, Capitulo, User, URLSalva


class IMangaRepository(ABC):
    """Interface para repositório de Mangás"""
    
    @abstractmethod
    def listar_todos(self) -> List[Manga]:
        """Retorna todos os mangás da biblioteca"""
        pass
    
    @abstractmethod
    def buscar_por_nome(self, nome: str) -> Optional[Manga]:
        """Busca um mangá pelo nome"""
        pass
    
    @abstractmethod
    def salvar(self, manga: Manga) -> Manga:
        """Salva ou atualiza um mangá"""
        pass
    
    @abstractmethod
    def deletar(self, nome: str) -> bool:
        """Deleta um mangá e todos seus capítulos"""
        pass
    
    @abstractmethod
    def existe(self, nome: str) -> bool:
        """Verifica se um mangá existe"""
        pass


class ICapituloRepository(ABC):
    """Interface para repositório de Capítulos"""
    
    @abstractmethod
    def listar_por_manga(self, manga_nome: str, ordem: str = 'asc') -> List[Capitulo]:
        """Lista todos os capítulos de um mangá"""
        pass
    
    @abstractmethod
    def buscar(self, manga_nome: str, numero: int) -> Optional[Capitulo]:
        """Busca um capítulo específico"""
        pass
    
    @abstractmethod
    def salvar(self, capitulo: Capitulo) -> Capitulo:
        """Salva um capítulo"""
        pass
    
    @abstractmethod
    def deletar(self, manga_nome: str, nome_arquivo: str) -> bool:
        """Deleta um capítulo específico"""
        pass
    
    @abstractmethod
    def existe(self, manga_nome: str, numero: int) -> bool:
        """Verifica se um capítulo existe"""
        pass
    
    @abstractmethod
    def contar_por_manga(self, manga_nome: str) -> int:
        """Conta quantos capítulos um mangá possui"""
        pass


class IUserRepository(ABC):
    """Interface para repositório de Usuários"""
    
    @abstractmethod
    def criar(self, user: User) -> User:
        """Cria um novo usuário"""
        pass
    
    @abstractmethod
    def buscar_por_username(self, username: str) -> Optional[User]:
        """Busca usuário pelo username"""
        pass
    
    @abstractmethod
    def buscar_por_id(self, user_id: int) -> Optional[User]:
        """Busca usuário pelo ID"""
        pass
    
    @abstractmethod
    def atualizar(self, user: User) -> User:
        """Atualiza dados do usuário"""
        pass
    
    @abstractmethod
    def existe(self, username: str) -> bool:
        """Verifica se usuário existe"""
        pass
    
    @abstractmethod
    def listar_todos(self) -> List[User]:
        """Lista todos os usuários"""
        pass


class IURLSalvaRepository(ABC):
    """Interface para repositório de URLs Salvas"""
    
    @abstractmethod
    def listar_todas(self) -> List[URLSalva]:
        """Lista todas as URLs salvas ativas"""
        pass
    
    @abstractmethod
    def buscar_por_nome(self, nome_manga: str) -> Optional[URLSalva]:
        """Busca URL por nome do mangá"""
        pass
    
    @abstractmethod
    def salvar(self, url: URLSalva) -> URLSalva:
        """Salva ou atualiza uma URL"""
        pass
    
    @abstractmethod
    def deletar(self, nome_manga: str) -> bool:
        """Deleta uma URL salva"""
        pass
    
    @abstractmethod
    def existe(self, nome_manga: str) -> bool:
        """Verifica se URL existe"""
        pass