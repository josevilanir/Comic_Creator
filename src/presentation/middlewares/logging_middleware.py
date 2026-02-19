"""
Middleware para logging de requests e erros
"""
import time
import logging
from flask import request, g
from functools import wraps


logger = logging.getLogger(__name__)


def setup_request_logging(app):
    """Configura logging de requests"""

    @app.before_request
    def log_request_start():
        g.start_time = time.time()
        logger.info(f"Iniciando {request.method} {request.path}")

    @app.after_request
    def log_request_end(response):
        duration = time.time() - getattr(g, "start_time", time.time())
        logger.info(
            f"Completado {request.method} {request.path} - Status: {response.status_code} - Duração: {duration:.3f}s"
        )
        return response

    @app.teardown_request
    def log_request_error(error=None):
        if error:
            logger.error(f"Erro na request {request.method} {request.path}: {error}")


def log_exceptions(f):
    """Decorator para logar exceções em funções"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Exceção em {f.__name__}: {e}")
            raise

    return wrapper
