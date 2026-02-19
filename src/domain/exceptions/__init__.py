"""
Exceções customizadas do domínio
"""
from .base_exceptions import (
    DomainException,
    EntityNotFoundException,
    ValidationException,
    DuplicateException,
)
from .manga_exceptions import (
    MangaNaoEncontradoException,
    MangaJaExisteException,
)
from .capitulo_exceptions import (
    CapituloNaoEncontradoException,
    CapituloInvalidoException,
)
from .download_exceptions import (
    DownloadException,
    URLInvalidaException,
    FalhaDownloadException,
)

from .compat_exceptions import (
    MangaNotFoundException,
    CapituloNotFoundException,
    CapituloJaExisteException,
    DownloadFailedException,
    ImagensInvalidasException,
    UserNotFoundException,
    InvalidCredentialsException,
    UserAlreadyExistsException,
    ArquivoNaoEncontradoException,
    AcessoNegadoException,
)

__all__ = [
    "DomainException",
    "EntityNotFoundException",
    "ValidationException",
    "DuplicateException",
    "MangaNaoEncontradoException",
    "MangaJaExisteException",
    "CapituloNaoEncontradoException",
    "CapituloInvalidoException",
    "DownloadException",
    "URLInvalidaException",
    "FalhaDownloadException",
]
