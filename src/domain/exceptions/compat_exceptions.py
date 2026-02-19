"""
Compat layer for old exception names used across the codebase.
This maps legacy exception names to new DomainException-based classes.
"""
from .base_exceptions import DomainException


class MangaNotFoundException(DomainException):
    def __init__(self, nome_manga: str):
        super().__init__(f"Mangá '{nome_manga}' não encontrado")
        self.nome_manga = nome_manga


class CapituloNotFoundException(DomainException):
    def __init__(self, numero: int, manga: str):
        super().__init__(f"Capítulo {numero} do mangá '{manga}' não encontrado")
        self.numero = numero
        self.manga = manga


class CapituloJaExisteException(DomainException):
    def __init__(self, numero: int, manga: str):
        super().__init__(f"Capítulo {numero} do mangá '{manga}' já existe")
        self.numero = numero
        self.manga = manga


class DownloadFailedException(DomainException):
    def __init__(self, url: str, motivo: str = ""):
        mensagem = f"Falha ao baixar de '{url}'"
        if motivo:
            mensagem += f": {motivo}"
        super().__init__(mensagem)
        self.url = url
        self.motivo = motivo


class ImagensInvalidasException(DomainException):
    def __init__(self, motivo: str = "Nenhuma imagem válida encontrada"):
        super().__init__(f"Validação de imagens falhou: {motivo}")
        self.motivo = motivo


class UserNotFoundException(DomainException):
    def __init__(self, username: str):
        super().__init__(f"Usuário '{username}' não encontrado")
        self.username = username


class InvalidCredentialsException(DomainException):
    def __init__(self):
        super().__init__("Credenciais inválidas")


class UserAlreadyExistsException(DomainException):
    def __init__(self, username: str):
        super().__init__(f"Usuário '{username}' já existe")
        self.username = username


class ArquivoNaoEncontradoException(DomainException):
    def __init__(self, caminho: str):
        super().__init__(f"Arquivo não encontrado: '{caminho}'")
        self.caminho = caminho


class AcessoNegadoException(DomainException):
    def __init__(self, recurso: str = ""):
        mensagem = "Acesso negado"
        if recurso:
            mensagem += f" ao recurso: '{recurso}'"
        super().__init__(mensagem)
        self.recurso = recurso
