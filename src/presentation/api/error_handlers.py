"""
Error Handlers Globais para a API
"""
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError
from src.domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    ValidationException as DomainValidationException,
    DuplicateException,
)


def register_error_handlers(app):
    """Registra todos os error handlers no Flask app"""

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "sucesso": False,
            "erro": "Recurso não encontrado",
            "codigo": "NOT_FOUND",
            "status": 404,
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        current_app.logger.error(f"Erro interno: {error}")
        return jsonify({
            "sucesso": False,
            "erro": "Erro interno do servidor",
            "codigo": "INTERNAL_ERROR",
            "status": 500,
        }), 500

    @app.errorhandler(HTTPException)
    def http_exception_handler(error):
        return jsonify({
            "sucesso": False,
            "erro": error.description,
            "codigo": error.name.upper().replace(" ", "_"),
            "status": error.code,
        }), error.code

    @app.errorhandler(EntityNotFoundException)
    def entity_not_found_handler(error):
        return jsonify({
            "sucesso": False,
            "erro": error.message,
            "codigo": error.code,
            "entidade": error.entity_name,
            "identificador": error.identifier,
            "status": 404,
        }), 404

    @app.errorhandler(DuplicateException)
    def duplicate_entity_handler(error):
        return jsonify({
            "sucesso": False,
            "erro": error.message,
            "codigo": error.code,
            "entidade": error.entity_name,
            "identificador": error.identifier,
            "status": 409,
        }), 409

    @app.errorhandler(DomainValidationException)
    def domain_validation_handler(error):
        response = {
            "sucesso": False,
            "erro": error.message,
            "codigo": error.code,
            "status": 400,
        }
        if getattr(error, "field", None):
            response["campo"] = error.field
        return jsonify(response), 400

    @app.errorhandler(ValidationError)
    def pydantic_validation_handler(error):
        return jsonify({
            "sucesso": False,
            "erro": "Dados inválidos",
            "codigo": "VALIDATION_ERROR",
            "detalhes": [
                {
                    "campo": ".".join(str(x) for x in err["loc"]),
                    "mensagem": err["msg"],
                    "tipo": err["type"],
                }
                for err in error.errors()
            ],
            "status": 400,
        }), 400

    @app.errorhandler(DomainException)
    def domain_exception_handler(error):
        return jsonify({
            "sucesso": False,
            "erro": error.message,
            "codigo": error.code,
            "status": 400,
        }), 400

    @app.errorhandler(Exception)
    def generic_exception_handler(error):
        current_app.logger.exception(f"Exceção não tratada: {error}")
        if current_app.config.get("DEBUG"):
            error_detail = str(error)
        else:
            error_detail = "Erro interno do servidor"
        return jsonify({
            "sucesso": False,
            "erro": error_detail,
            "codigo": "INTERNAL_ERROR",
            "status": 500,
        }), 500
