"""
Interfaces de Repositórios - Contratos para acesso a dados
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Set
from ..entities import Manga, Capitulo, User, URLSalva


class IMangaRepository(ABC):
    """Interface para repositório de Mangás"""
    
    @abstractmethod
    def listar_todos(self, user_id: int, skip: int = 0, limit: Optional[int] = None) -> List[Manga]:
        """Retorna os mangás da biblioteca do usuário com paginação"""
        pass

    @abstractmethod
    def contar_todos(self, user_id: int) -> int:
        """Retorna o total de mangás do usuário"""
        pass
    
    @abstractmethod
    def buscar_por_nome(self, user_id: int, nome: str) -> Optional[Manga]:
        """Busca um mangá pelo nome para um usuário específico"""
        pass
    
    @abstractmethod
    def salvar(self, user_id: int, manga: Manga) -> Manga:
        """Salva ou atualiza um mangá para um usuário"""
        pass
    
    @abstractmethod
    def deletar(self, user_id: int, nome: str) -> bool:
        """Deleta um mangá e todos seus capítulos"""
        pass
    
    @abstractmethod
    def existe(self, user_id: int, nome: str) -> bool:
        """Verifica se um mangá existe para o usuário"""
        pass


class ICapituloRepository(ABC):
    """Interface para repositório de Capítulos"""
    
    @abstractmethod
    def listar_por_manga(self, user_id: int, manga_nome: str, ordem: str = 'asc') -> List[Capitulo]:
        """Lista todos os capítulos de um mangá"""
        pass
    
    @abstractmethod
    def buscar(self, user_id: int, manga_nome: str, numero: int) -> Optional[Capitulo]:
        """Busca um capítulo específico"""
        pass
    
    @abstractmethod
    def salvar(self, user_id: int, capitulo: Capitulo) -> Capitulo:
        """Salva um capítulo"""
        pass
    
    @abstractmethod
    def deletar(self, user_id: int, manga_nome: str, nome_arquivo: str) -> bool:
        """Deleta um capítulo específico"""
        pass
    
    @abstractmethod
    def existe(self, user_id: int, manga_nome: str, numero: int) -> bool:
        """Verifica se um capítulo existe"""
        pass
    
    @abstractmethod
    def contar_por_manga(self, user_id: int, manga_nome: str) -> int:
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

    @abstractmethod
    def limpar_tokens_antigos(self, user_id: Optional[int] = None):
        """Remove tokens revogados ou expirados"""
        pass


class IURLSalvaRepository(ABC):
    """Interface para repositório de URLs Salvas"""
    
    @abstractmethod
    def listar_todas(self, user_id: int) -> List[URLSalva]:
        """Lista todas as URLs salvas ativas do usuário"""
        pass
    
    @abstractmethod
    def buscar_por_nome(self, user_id: int, nome_manga: str) -> Optional[URLSalva]:
        """Busca URL por nome do mangá"""
        pass
    
    @abstractmethod
    def salvar(self, user_id: int, url: URLSalva) -> URLSalva:
        """Salva ou atualiza uma URL"""
        pass
    
    @abstractmethod
    def deletar(self, user_id: int, nome_manga: str) -> bool:
        """Deleta uma URL salva"""
        pass
    
    @abstractmethod
    def existe(self, user_id: int, nome_manga: str) -> bool:
        """Verifica se URL existe"""
        pass

class IUserDataRepository(ABC):
    """Interface para leituras e progresso (SQLite)"""
    @abstractmethod
    def toggle_read(self, user_id: int, manga_name: str, filename: str) -> bool: pass
    @abstractmethod
    def get_reads(self, user_id: int, manga_name: str) -> Set[str]: pass
    @abstractmethod
    def get_progress(self, user_id: int, manga_name: str, filename: str) -> int: pass
    @abstractmethod
    def save_progress(self, user_id: int, manga_name: str, filename: str, page: int): pass
