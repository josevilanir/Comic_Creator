"""
Exceções de Download
"""
from .base_exceptions import DomainException, ValidationException


class DownloadException(DomainException):
    """Erro genérico de download"""
    def __init__(self, message: str):
        super().__init__(message, code="DOWNLOAD_ERROR")


class URLInvalidaException(ValidationException):
    """URL inválida para download"""
    def __init__(self, url: str):
        message = f"URL inválida: {url}"
        super().__init__(message)
        self.url = url


class FalhaDownloadException(DownloadException):
    """Falha ao baixar conteúdo"""
    def __init__(self, url: str, motivo: str):
        message = f"Falha ao baixar de {url}: {motivo}"
        super().__init__(message)
        self.url = url
        self.motivo = motivo
