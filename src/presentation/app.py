"""
Criação da aplicação Flask
"""
from flask import Flask
from flask_cors import CORS
from config.settings import config
from config.dependencies import DependencyContainer
from src.presentation.api.error_handlers import register_error_handlers
from src.presentation.middlewares.logging_middleware import setup_request_logging


def create_app(env='development'):
    """Factory da aplicação Flask"""
    app = Flask(__name__, template_folder='../../templates', static_folder='../../static')

    # Carregar configurações
    app.config.from_object(config[env])
    config[env].init_app(app)

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Dependency Injection
    container = DependencyContainer(config[env])
    app.config['DI_CONTAINER'] = container
    app.container = container

    # Registrar Error Handlers
    register_error_handlers(app)

    # Setup Logging
    setup_request_logging(app)

    from src.presentation.api.routes import api_bp
    app.register_blueprint(api_bp)

    # Registrar Controllers (templates Jinja2)
    from src.presentation.controllers.download_controller import download_bp
    from src.presentation.controllers.manga_controller import manga_bp
    from src.presentation.controllers.capitulo_controller import capitulo_bp
    from src.presentation.controllers.auth_controller import auth_bp

    app.register_blueprint(download_bp)
    app.register_blueprint(manga_bp, url_prefix='/manga')
    app.register_blueprint(capitulo_bp, url_prefix='/capitulo')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Rota de health check
    @app.route('/health')
    def health():
        return {'status': 'ok', 'ambiente': env}, 200

    return app