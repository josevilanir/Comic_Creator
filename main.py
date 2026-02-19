"""
Entry point da aplicação Comic Creator
"""
from config.settings import config
from config.dependencies import DependencyContainer
from src.presentation.app import create_app
import os

# Determina ambiente
env = os.environ.get('FLASK_ENV', 'development')

# Cria aplicação com DI
container = DependencyContainer(config[env])
app = create_app(container)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )