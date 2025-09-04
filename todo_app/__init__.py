from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from .extensions import db
from .todos.routes import bp as todos_bp
from .config import get_config
from .api_docs import api
import os
import logging
from typing import Optional


def create_app(config_object: Optional[str] = None) -> Flask:
    """
    Factory function to create Flask app instance.
    Can accept config class name or use default.
    """

    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    if config_object:
        config_class = get_config(config_object)
    else:
        config_class = get_config()

    app.config.from_object(config_class)

    # Initialize rate limiter
    default_limits = app.config.get("RATELIMIT_DEFAULT")
    if default_limits is None:
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            storage_uri=app.config.get("RATELIMIT_STORAGE_URL", "memory://")
        )
    else:
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[default_limits] if isinstance(default_limits, str) else default_limits,
            storage_uri=app.config.get("RATELIMIT_STORAGE_URL", "memory://")
        )

    # Initialize CORS
    cors_origins = app.config.get("CORS_ORIGINS")
    if cors_origins is None:
        cors_origins = ["*"]
    CORS(app, origins=cors_origins)

    # Setup logging
    log_level = app.config.get("LOG_LEVEL", "INFO")
    if not isinstance(log_level, int):
        log_level = getattr(logging, log_level.upper(), logging.INFO)

    log_format = app.config.get("LOG_FORMAT")
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format
    )
    app.logger.setLevel(log_level)

    # Initialize database extension
    try:
        db.init_app(app)
    except Exception as e:
        app.logger.error(f"Error initializing database: {e}")
        raise

    # Register todos blueprint
    app.register_blueprint(todos_bp, url_prefix="/api/todos")

    # Initialize API documentation
    api.init_app(app)

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
