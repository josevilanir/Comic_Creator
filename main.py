"""
Entry point da aplicação Comic Creator
"""
from src.presentation.app import create_app
import os

# Determina ambiente
env = os.environ.get('FLASK_ENV', 'development')

# Cria aplicação
app = create_app(env)

# Expose config variables for tests
BASE_COMICS = app.config.get('BASE_COMICS', os.path.expanduser('~/Comics'))
THUMBNAILS = app.config.get('THUMBNAILS', os.path.join('static', 'thumbnails'))
URLS_JSON = os.path.join(os.path.dirname(__file__), 'urls_salvas.json')

# Ensure the app knows the absolute path to the saved-urls file (used by carregar_urls)
app.config['URLS_JSON'] = URLS_JSON

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )