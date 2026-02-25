"""
Error Handlers Globais da API — formato JSend
"""
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError
from src.domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    ValidationException as DomainValidationException,
    DuplicateException,
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)


def _error(message, code, status_code):
    """Helper interno JSend error."""
    return jsonify({"status": "error", "message": message, "code": code}), status_code


def register_error_handlers(app):
    """Registra todos os error handlers no Flask app"""

    @app.errorhandler(404)
    def not_found_error(e):
        return _error("Recurso não encontrado", "NOT_FOUND", 404)

    @app.errorhandler(500)
    def internal_error(e):
        current_app.logger.error(f"Erro interno: {e}")
        return _error("Erro interno do servidor", "INTERNAL_ERROR", 500)

    @app.errorhandler(HTTPException)
    def http_exception_handler(e):
        return _error(e.description, e.name.upper().replace(" ", "_"), e.code)

    @app.errorhandler(EntityNotFoundException)
    def entity_not_found_handler(e):
        return _error(e.message, e.code, 404)

    @app.errorhandler(UserNotFoundException)
    def user_not_found_handler(e):
        return _error(e.message, "USER_NOT_FOUND", 404)

    @app.errorhandler(DuplicateException)
    def duplicate_entity_handler(e):
        return _error(e.message, e.code, 409)

    @app.errorhandler(UserAlreadyExistsException)
    def user_already_exists_handler(e):
        return _error(e.message, "USER_ALREADY_EXISTS", 409)

    @app.errorhandler(InvalidCredentialsException)
    def invalid_credentials_handler(e):
        return _error(e.message, "INVALID_CREDENTIALS", 401)

    @app.errorhandler(DomainValidationException)
    def domain_validation_handler(e):
        return _error(e.message, e.code, 400)

    @app.errorhandler(ValidationError)
    def pydantic_validation_handler(e):
        return _error("Dados inválidos", "VALIDATION_ERROR", 400)

    @app.errorhandler(DomainException)
    def domain_exception_handler(e):
        return _error(e.message, e.code, 400)

    @app.errorhandler(Exception)
    def generic_exception_handler(e):
        current_app.logger.exception(f"Exceção não tratada: {e}")
        if current_app.config.get("DEBUG"):
            error_detail = str(e)
        else:
            error_detail = "Erro interno do servidor"
        return _error(error_detail, "INTERNAL_ERROR", 500)
