from flask import Flask
from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app

