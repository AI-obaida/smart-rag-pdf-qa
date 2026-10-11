import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

from app.config import config

db = SQLAlchemy()


def create_app(config_name=None, test_config=None):
    app = Flask(
        __name__,
        template_folder="frontend/templates",
    )

    environment = config_name or os.environ.get(
        "APP_ENV", "development"
    )

    if environment not in config:
        raise ValueError("Unknown application environment")

    app.config.from_object(config[environment])

    if test_config is not None:
        app.config.update(test_config)

    if environment == "production" and not app.config["SECRET_KEY"]:
        raise RuntimeError(
            "SECRET_KEY must be configured in production"
        )

    db.init_app(app)

    from app.endpoints.upload import upload_bp
    from app.endpoints.ask import ask_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(ask_bp)
    from app.endpoints.documents import documents_bp
    app.register_blueprint(documents_bp)

    @app.get("/")
    def index():
        return render_template("index.html")

    return app
