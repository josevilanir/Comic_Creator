"""
Exceções base do domínio
"""


class DomainException(Exception):
    """Exceção base do domínio"""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class EntityNotFoundException(DomainException):
    """Entidade não encontrada"""
    def __init__(self, entity_name: str, identifier: str):
        message = f"{entity_name} '{identifier}' não encontrado(a)"
        super().__init__(message, code="NOT_FOUND")
        self.entity_name = entity_name
        self.identifier = identifier


class ValidationException(DomainException):
    """Erro de validação de dados"""
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class DuplicateException(DomainException):
    """Entidade duplicada"""
    def __init__(self, entity_name: str, identifier: str):
        message = f"{entity_name} '{identifier}' já existe"
        super().__init__(message, code="DUPLICATE")
        self.entity_name = entity_name
        self.identifier = identifier
