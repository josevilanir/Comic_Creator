"""
Exceções customizadas do domínio
"""


class DomainException(Exception):
    """Exceção base para erros de domínio"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class MangaNotFoundException(DomainException):
    """Mangá não encontrado"""
    def __init__(self, nome_manga: str):
        super().__init__(f"Mangá '{nome_manga}' não encontrado")
        self.nome_manga = nome_manga


class CapituloNotFoundException(DomainException):
    """Capítulo não encontrado"""
    def __init__(self, numero: int, manga: str):
        super().__init__(f"Capítulo {numero} do mangá '{manga}' não encontrado")
        self.numero = numero
        self.manga = manga


class CapituloJaExisteException(DomainException):
    """Capítulo já existe no sistema"""
    def __init__(self, numero: int, manga: str):
        super().__init__(f"Capítulo {numero} do mangá '{manga}' já existe")
        self.numero = numero
        self.manga = manga


class DownloadFailedException(DomainException):
    """Falha no download de capítulo"""
    def __init__(self, url: str, motivo: str = ""):
        mensagem = f"Falha ao baixar de '{url}'"
        if motivo:
            mensagem += f": {motivo}"
        super().__init__(mensagem)
        self.url = url
        self.motivo = motivo


class ImagensInvalidasException(DomainException):
    """Imagens baixadas não são válidas para capítulo"""
    def __init__(self, motivo: str = "Nenhuma imagem válida encontrada"):
        super().__init__(f"Validação de imagens falhou: {motivo}")
        self.motivo = motivo


class URLInvalidaException(DomainException):
    """URL fornecida é inválida"""
    def __init__(self, url: str):
        super().__init__(f"URL inválida: '{url}'")
        self.url = url


class UserNotFoundException(DomainException):
    """Usuário não encontrado"""
    def __init__(self, username: str):
        super().__init__(f"Usuário '{username}' não encontrado")
        self.username = username


class InvalidCredentialsException(DomainException):
    """Credenciais inválidas"""
    def __init__(self):
        super().__init__("Credenciais inválidas")


class UserAlreadyExistsException(DomainException):
    """Usuário já existe no sistema"""
    def __init__(self, username: str):
        super().__init__(f"Usuário '{username}' já existe")
        self.username = username


class ArquivoNaoEncontradoException(DomainException):
    """Arquivo não encontrado no sistema de arquivos"""
    def __init__(self, caminho: str):
        super().__init__(f"Arquivo não encontrado: '{caminho}'")
        self.caminho = caminho


class AcessoNegadoException(DomainException):
    """Acesso negado a recurso"""
    def __init__(self, recurso: str = ""):
        mensagem = "Acesso negado"
        if recurso:
            mensagem += f" ao recurso: '{recurso}'"
        super().__init__(mensagem)
        self.recurso = recurso