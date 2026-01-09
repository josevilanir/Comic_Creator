"""
Infrastructure Repositories - Implementações de repositórios
"""
from .filesystem_manga_repository import FileSystemMangaRepository
from .filesystem_capitulo_repository import FileSystemCapituloRepository
from .sqlite_user_repository import SQLiteUserRepository
from .json_url_repository import JSONURLRepository

__all__ = [
    'FileSystemMangaRepository',
    'FileSystemCapituloRepository',
    'SQLiteUserRepository',
    'JSONURLRepository',
]