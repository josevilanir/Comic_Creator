import os
import sys

# Ensure backend folder is on sys.path so we can import the moved package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from comic_creator import create_app
from comic_creator.downloader import baixar_capitulo_para_pdf

app = create_app()

# Expose config variables for tests
BASE_COMICS = app.config.get('BASE_COMICS', os.path.expanduser('~/Comics'))
THUMBNAILS = app.config.get('THUMBNAILS', os.path.join('static', 'thumbnails'))
URLS_JSON = os.path.join(os.path.dirname(__file__), 'urls_salvas.json')

# Ensure the app knows the absolute path to the saved-urls file (used by carregar_urls)
app.config['URLS_JSON'] = URLS_JSON

if __name__ == '__main__':
    app.run(debug=True)