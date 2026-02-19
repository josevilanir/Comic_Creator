"""
Configuração de Logging
"""
import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """Configura sistema de logging"""

    # Criar diretório de logs
    import os
    os.makedirs('logs', exist_ok=True)

    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # File Handler (rotativo)
    file_handler = RotatingFileHandler(
        'logs/app.log', maxBytes=10 * 1024 * 1024, backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Error File Handler
    error_handler = RotatingFileHandler(
        'logs/errors.log', maxBytes=10 * 1024 * 1024, backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # Configurar app logger
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)
