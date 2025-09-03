from flask import Flask
from .extensions import db
from .todos.routes import bp as todos_bp
import os
import logging
from typing import Optional


def create_app(config_object: Optional[str] = None) -> Flask:
    """
    Factory function to create Flask app instance.
    Can accept config class name or use default.
    """

    app = Flask(__name__, instance_relative_config=True)

    # Validate and configure SECRET_KEY (required for security)
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise ValueError(
            "SECRET_KEY not found! "
            "Please set environment variable SECRET_KEY or create .env file in instance/ folder. "
            "See instance/.env.example for example configuration."
        )

    # Basic app configuration
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///data.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=os.environ.get("FLASK_DEBUG", "1") == "1",
    )

    # Setup logging
    logging.basicConfig(level=logging.DEBUG if app.config["DEBUG"] else logging.INFO)
    app.logger.setLevel(logging.DEBUG if app.config["DEBUG"] else logging.INFO)

    # Initialize database extension
    try:
        db.init_app(app)
    except Exception as e:
        app.logger.error(f"Error initializing database: {e}")
        raise

    # Register todos blueprint
    app.register_blueprint(todos_bp, url_prefix="/api/todos")

    # Health check endpoint
    @app.route("/health")
    def health():
        """
        Endpoint to check app status.
        """
        return {"status": "ok"}

    # Auto create tables on first run (only for development,
    # use migrations in production)
    with app.app_context():
        db.create_all()

    return app
