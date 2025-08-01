import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'segredo')
    BASE_COMICS = os.environ.get('BASE_COMICS', os.path.expanduser('~/Comics'))
    THUMBNAIL_DIR = os.environ.get('THUMBNAIL_DIR', os.path.join('static', 'thumbnails'))
