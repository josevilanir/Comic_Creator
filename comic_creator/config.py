import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'segredo')
    BASE_COMICS = os.path.expanduser('~/Comics')
    THUMBNAILS = os.path.join('static', 'thumbnails')
    URLS_JSON = 'urls_salvas.json'

    @staticmethod
    def init_app(app):
        os.makedirs(Config.BASE_COMICS, exist_ok=True)
        os.makedirs(Config.THUMBNAILS, exist_ok=True)

