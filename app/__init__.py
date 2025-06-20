# app/__init__.py
import os
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "segredo")

    # Diretório base dos mangás
    base_dir = os.path.expanduser("~/Comics")
    os.makedirs(base_dir, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = base_dir
    app.config["BASE_DIR"] = base_dir

    from . import routes
    app.register_blueprint(routes.bp)

    return app
