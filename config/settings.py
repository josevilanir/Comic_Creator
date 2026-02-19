"""
Configurações da aplicação
"""
import os
from pathlib import Path


class Config:
    """Configurações base"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    
    # Diretórios
    BASE_DIR = Path(__file__).parent.parent
    BASE_COMICS = os.environ.get('BASE_COMICS', str(Path.home() / 'Comics'))
    THUMBNAIL_DIR = os.path.join(BASE_COMICS, '.thumbnails')
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'comic_creator.db')
    
    # URLs
    URLS_JSON = os.environ.get('URLS_JSON', 'urls_salvas.json')
    
    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    @staticmethod
    def init_app(app):
        """Inicializa configurações"""
        os.makedirs(Config.BASE_COMICS, exist_ok=True)
        os.makedirs(Config.THUMBNAIL_DIR, exist_ok=True)


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}