"""
Exceções específicas de Manga
"""
from .base_exceptions import EntityNotFoundException, DuplicateException


class MangaNaoEncontradoException(EntityNotFoundException):
    """Mangá não encontrado"""
    def __init__(self, nome: str):
        super().__init__("Mangá", nome)


class MangaJaExisteException(DuplicateException):
    """Mangá já existe"""
    def __init__(self, nome: str):
        super().__init__("Mangá", nome)
