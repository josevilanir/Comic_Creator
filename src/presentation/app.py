"""
Criação da aplicação Flask
"""
from flask import Flask, jsonify  
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
    CORS(app, resources={
        r"/api/*":      {"origins": "*", "supports_credentials": False},
        r"/api/v1/*":   {"origins": "*", "supports_credentials": False},
        r"/capitulo/*": {"origins": "*", "supports_credentials": False},
        r"/manga/*":    {"origins": "*", "supports_credentials": False},
    })
    # Dependency Injection
    container = DependencyContainer(config[env])
    app.config['DI_CONTAINER'] = container
    app.container = container

    # Registrar Error Handlers
    register_error_handlers(app)

    # Setup Logging
    setup_request_logging(app)

    # Registrar API REST
    from src.presentation.api.routes import api_bp
    app.register_blueprint(api_bp)

    from src.presentation.api.progresso_routes import progresso_bp
    app.register_blueprint(progresso_bp)

    # Aliases de retrocompatibilidade — /api/* → /api/v1/*
    # TODO: remover após todos os clientes migrarem para /api/v1
    from flask import redirect

    @app.route('/api/library')
    @app.route('/api/library/<path:resto>')
    def compat_library(resto=''):
        """TODO: remover após todos os clientes migrarem para /api/v1"""
        path = f'/api/v1/library/{resto}' if resto else '/api/v1/library'
        return redirect(path, code=308)

    @app.route('/api/urls', methods=['GET', 'POST', 'DELETE'])
    @app.route('/api/urls/<path:resto>', methods=['GET', 'POST', 'DELETE'])
    def compat_urls(resto=''):
        """TODO: remover após todos os clientes migrarem para /api/v1"""
        path = f'/api/v1/urls/{resto}' if resto else '/api/v1/urls'
        return redirect(path, code=308)

    @app.route('/api/download', methods=['GET', 'POST'])
    @app.route('/api/download/<path:resto>', methods=['GET', 'POST', 'DELETE'])
    def compat_download(resto=''):
        """TODO: remover após todos os clientes migrarem para /api/v1"""
        path = f'/api/v1/download/{resto}' if resto else '/api/v1/download'
        return redirect(path, code=308)

    # Registrar Controllers (templates Jinja2)
    from src.presentation.controllers.download_controller import download_bp
    from src.presentation.controllers.manga_controller import manga_bp
    from src.presentation.controllers.capitulo_controller import capitulo_bp
    from src.presentation.controllers.auth_controller import auth_bp

    app.register_blueprint(download_bp, url_prefix='/legacy')
    app.register_blueprint(manga_bp, url_prefix='/manga')
    app.register_blueprint(capitulo_bp, url_prefix='/capitulo')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # ========================================
    # ✅ ADICIONE ESTAS ROTAS AQUI:
    # ========================================
    
    @app.route('/')
    def index():
        """Rota raiz - Informações da API"""
        return jsonify({
            'application': 'Comic Creator API',
            'version': '2.0.0',
            'status': 'running',
            'environment': env,
            'endpoints': {
                'health': '/health',
                'api_root': '/api/v1',
                'library': '/api/v1/library',
                'manga_details': '/api/v1/library/<manga_name>',
                'urls': '/api/v1/urls',
                'download': '/api/v1/download'
            },
            'frontend': {
                'url': 'http://localhost:5173',
                'description': 'Acesse o frontend React para usar a aplicação completa'
            },
            'documentation': {
                'readme': 'https://github.com/seu-usuario/Comic_Creator',
                'endpoints': 'Acesse /api para ver lista completa de endpoints'
            },
            'server_info': {
                'debug': app.config['DEBUG'],
                'testing': app.config['TESTING']
            }
        })
    
    @app.route('/api')
    def api_root():
        """Rota raiz da API - Documentação de endpoints"""
        return jsonify({
            'message': 'Comic Creator REST API',
            'version': '1.0.0',
            'base_url': '/api/v1',
            'endpoints': [
                {
                    'method': 'GET',
                    'path': '/api/v1/library',
                    'description': 'Lista todos os mangás da biblioteca',
                    'response': 'Array de objetos Manga'
                },
                {
                    'method': 'GET',
                    'path': '/api/v1/library/<manga_name>',
                    'description': 'Lista capítulos de um mangá específico',
                    'params': {'manga_name': 'Nome do mangá', 'ordem': 'asc ou desc'},
                    'response': 'Objeto com manga e array de capítulos'
                },
                {
                    'method': 'GET',
                    'path': '/api/v1/urls',
                    'description': 'Lista todas as URLs salvas',
                    'response': 'Objeto {nome_manga: url_base}'
                },
                {
                    'method': 'POST',
                    'path': '/api/v1/urls',
                    'description': 'Salva uma nova URL base',
                    'body': {'nome': 'string', 'url': 'string'},
                    'response': 'Objeto com success e message'
                },
                {
                    'method': 'DELETE',
                    'path': '/api/v1/urls',
                    'description': 'Remove uma URL salva',
                    'body': {'nome': 'string'},
                    'response': 'Objeto com success e message'
                },
                {
                    'method': 'POST',
                    'path': '/api/v1/download',
                    'description': 'Inicia o download de um capítulo',
                    'body': {
                        'base_url': 'string',
                        'capitulo': 'number',
                        'nome_manga': 'string'
                    },
                    'response': 'Objeto with success and message'
                },
                {
                    'method': 'GET',
                    'path': '/health',
                    'description': 'Verifica o status da API',
                    'response': 'Objeto com status e ambiente'
                }
            ],
            'authentication': 'Não requerida atualmente',
            'rate_limits': 'Não implementado'
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'ambiente': env,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }), 200

    return app