import os
from flask import Flask, render_template, g, request
from .config import Config
from .db import init_db


def create_app(config_class=Config):
    app = Flask(
        __name__, template_folder="../templates", static_folder="../static"
    )
    app.config.from_object(config_class)
    # Ensure URLS_JSON points to the project root file by default
    project_root_urls = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'urls_salvas.json'))
    app.config.setdefault('URLS_JSON', project_root_urls)
    config_class.init_app(app)
    
    init_db(app)

    from .routes import bp
    app.register_blueprint(bp)

    # Add simple CORS headers for API routes to allow frontend dev access
    @app.after_request
    def add_cors_headers(response):
        try:
            # Allow CORS for API and visualization endpoints (PDFs/images) during development
            if request.path.startswith(('/api/', '/visualizar')):
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PUT,OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
        except Exception:
            pass
        return response

    @app.before_request
    def load_logged_in_user():
        g.user = None

    @app.route("/login")
    def login():
        return render_template("login.html")

    return app
