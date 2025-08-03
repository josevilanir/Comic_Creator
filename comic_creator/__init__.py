from flask import Flask, render_template
from .config import Config


def create_app(config_class=Config):
    app = Flask(
        __name__, template_folder="../templates", static_folder="../static"
    )
    app.config.from_object(config_class)
    config_class.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    @app.route("/login")
    def login():
        return render_template("login.html")

    return app

