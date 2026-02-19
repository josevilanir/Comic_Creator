"""
Exceções específicas de Capítulo
"""
from .base_exceptions import EntityNotFoundException, ValidationException


class CapituloNaoEncontradoException(EntityNotFoundException):
    """Capítulo não encontrado"""
    def __init__(self, manga: str, numero: int):
        identifier = f"{manga} - Cap. {numero}"
        super().__init__("Capítulo", identifier)
        self.manga = manga
        self.numero = numero


class CapituloInvalidoException(ValidationException):
    """Capítulo com dados inválidos"""
    def __init__(self, message: str):
        super().__init__(message)
