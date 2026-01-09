"""
Criação da aplicação Flask
"""
from flask import Flask
from config.dependencies import DependencyContainer
from config.settings import config


def create_app(config_name='default'):
    """
    Factory da aplicação Flask
    
    Args:
        config_name: Nome da configuração ('development', 'production', 'default')
        
    Returns:
        Aplicação Flask configurada
    """
    app = Flask(
        __name__,
        template_folder='../../templates',
        static_folder='../../static'
    )
    
    # Carrega configurações no Flask
    config_class = config[config_name]
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Instância do seu Config (pra DI/container)
    domain_config = config_class()          # <- isso aqui é o pulo do gato
    app.container = DependencyContainer(domain_config)

    
    # Registra blueprints
    from .controllers.download_controller import download_bp
    from .controllers.manga_controller import manga_bp
    from .controllers.capitulo_controller import capitulo_bp
    from .controllers.auth_controller import auth_bp
    
    app.register_blueprint(download_bp)
    app.register_blueprint(manga_bp, url_prefix='/manga')
    app.register_blueprint(capitulo_bp, url_prefix='/capitulo')
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    
    return app