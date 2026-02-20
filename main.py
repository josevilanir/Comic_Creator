"""
Entry point da aplicação Comic Creator
"""
from src.presentation.app import create_app
import os

# Determina ambiente
env = os.environ.get('FLASK_ENV', 'development')

# Cria aplicação (create_app já cria o container internamente)
app = create_app(env)  # ✅ Passa apenas o env

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )