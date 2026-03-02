# app/__init__.py
import os
from flask import Flask
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Diretório base dos mangás e thumbnails
    base_dir = app.config["BASE_COMICS"]
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(app.config["THUMBNAIL_DIR"], exist_ok=True)
    app.secret_key = app.config["SECRET_KEY"]
    app.config["UPLOAD_FOLDER"] = base_dir
    app.config["BASE_DIR"] = base_dir

    from . import routes
    app.register_blueprint(routes.bp)

    return app
