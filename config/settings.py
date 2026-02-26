"""
Configurações da aplicação Comic Creator
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar arquivo .env se existir
load_dotenv()

class Config:
    """Configurações base"""
    
    # Diretórios principais
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    TESTING = False
    
    # Diretórios de conteúdo
    BASE_COMICS = Path(os.environ.get('BASE_COMICS', str(Path.home() / 'Comics')))
    THUMBNAIL_DIR = BASE_COMICS / '.thumbnails'
    
    # Database
    DATABASE_PATH = str(DATA_DIR / 'comic_creator.db')
    
    # URLs e dados persistentes
    URLS_JSON = str(DATA_DIR / 'urls_salvas.json')
    
    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = str(LOGS_DIR / 'app.log')
    ERROR_LOG_FILE = str(LOGS_DIR / 'errors.log')
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # Download
    DOWNLOAD_TIMEOUT = 30  # segundos
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # segundos
    
    # Segurança
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # CORS
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000']

    # Object Storage — S3 / Cloudflare R2
    # Define S3_BUCKET para ativar o modo S3 (repos de manga/capitulo usam S3).
    # Deixe em branco para usar o filesystem local (desenvolvimento/VPS).
    # Para Cloudflare R2: S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
    #                     S3_REGION=auto
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL', '')
    S3_ACCESS_KEY   = os.environ.get('S3_ACCESS_KEY', '')
    S3_SECRET_KEY   = os.environ.get('S3_SECRET_KEY', '')
    S3_BUCKET       = os.environ.get('S3_BUCKET', '')
    S3_REGION       = os.environ.get('S3_REGION', 'auto')
    S3_PRESIGNED_EXPIRY = int(os.environ.get('S3_PRESIGNED_EXPIRY', '3600'))  # segundos
    
    @staticmethod
    def init_app(app):
        """Inicializa configurações e cria diretórios necessários"""
        # Criar diretórios
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        os.makedirs(Config.BASE_COMICS, exist_ok=True)
        os.makedirs(Config.THUMBNAIL_DIR, exist_ok=True)
        
        # Log de inicialização
        app.logger.info(f'Aplicação inicializada')
        app.logger.info(f'BASE_DIR: {Config.BASE_DIR}')
        app.logger.info(f'DATA_DIR: {Config.DATA_DIR}')
        app.logger.info(f'BASE_COMICS: {Config.BASE_COMICS}')
        app.logger.info(f'DATABASE: {Config.DATABASE_PATH}')


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    
    # CORS mais permissivo em dev
    CORS_ORIGINS = ['*']
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.info('🔧 Modo DEVELOPMENT ativado')
        app.logger.debug('Debug mode: ON')


class TestingConfig(Config):
    """Configurações de testes"""
    TESTING = True
    DEBUG = True
    
    # Usa diretórios temporários para testes
    import tempfile
    DATA_DIR = Path(tempfile.mkdtemp()) / 'test_data'
    BASE_COMICS = Path(tempfile.mkdtemp()) / 'test_comics'
    THUMBNAIL_DIR = BASE_COMICS / '.thumbnails'
    
    # Database em memória
    DATABASE_PATH = ':memory:'
    
    # URLs JSON temporário
    URLS_JSON = str(DATA_DIR / 'test_urls.json')
    
    # Logs de teste
    LOGS_DIR = Path(tempfile.mkdtemp()) / 'test_logs'
    LOG_FILE = str(LOGS_DIR / 'test_app.log')
    ERROR_LOG_FILE = str(LOGS_DIR / 'test_errors.log')
    
    # Desabilita limitações em testes
    MAX_CONTENT_LENGTH = None
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.info('🧪 Modo TESTING ativado')


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    
    # Segurança reforçada
    SESSION_COOKIE_SECURE = True  # Requer HTTPS
    
    # CORS restrito em produção — ex: CORS_ORIGINS=https://meusite.com,https://www.meusite.com
    CORS_ORIGINS = [o.strip() for o in os.environ.get('CORS_ORIGINS', '').split(',') if o.strip()]

    # Secret key DEVE ser definida em produção
    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Valida configurações críticas
        if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            raise ValueError(
                '🚨 ERRO: SECRET_KEY não definida em produção! '
                'Defina a variável de ambiente SECRET_KEY.'
            )

        if not app.config['CORS_ORIGINS']:
            raise ValueError(
                '🚨 ERRO: CORS_ORIGINS não definida em produção! '
                'Ex: CORS_ORIGINS=https://meusite.com,https://www.meusite.com'
            )

        app.logger.info('🚀 Modo PRODUCTION ativado')
        app.logger.info(f'CORS permitido para: {app.config["CORS_ORIGINS"]}')
        app.logger.warning('Certifique-se de usar HTTPS em produção!')


# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env_name: str = None) -> Config:
    """
    Retorna a configuração apropriada baseada no ambiente.
    
    Args:
        env_name: Nome do ambiente ('development', 'testing', 'production')
                 Se None, usa FLASK_ENV ou 'development'
    
    Returns:
        Classe de configuração apropriada
    """
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env_name, config['default'])