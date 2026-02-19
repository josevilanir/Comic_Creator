"""
Domain Repositories - Interfaces de repositórios
"""
from .interfaces import (
    IMangaRepository,
    ICapituloRepository,
    IUserRepository,
    IURLSalvaRepository
)

__all__ = [
    'IMangaRepository',
    'ICapituloRepository', 
    'IUserRepository',
    'IURLSalvaRepository'
]