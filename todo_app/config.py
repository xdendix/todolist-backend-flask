"""
Configuration management for different environments.
"""
import os
from typing import Optional


class Config:
    """Base configuration class."""

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    DEBUG = False
    TESTING = False

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///data.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pagination settings
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 10
    MAX_PER_PAGE = 100

    # Rate limiting (if using Flask-Limiter)
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # CORS settings
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5000"]

    # API settings
    API_TITLE = "Todo API"
    API_VERSION = "v1"
    API_DESCRIPTION = "A RESTful API for managing todos"

    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    LOG_LEVEL = "DEBUG"

    # Allow all origins in development
    CORS_ORIGINS = ["*"]

    # More permissive rate limiting in development
    RATELIMIT_DEFAULT = "1000 per hour"


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"

    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Disable rate limiting in tests
    RATELIMIT_DEFAULT = None

    # Allow all origins in testing
    CORS_ORIGINS = ["*"]


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    LOG_LEVEL = "WARNING"

    # Ensure SECRET_KEY is set in production
    @property
    def SECRET_KEY(self):
        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        return secret_key

    # Ensure DATABASE_URL is set in production
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable must be set in production")

        # Fix for Railway postgres:// -> postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        return database_url

    # Stricter rate limiting in production
    RATELIMIT_DEFAULT = "100 per hour"

    # More restrictive CORS in production
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",") if os.environ.get("CORS_ORIGINS") else []


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration class based on environment.

    Priority order:
    1. Explicit config_name parameter
    2. FLASK_ENV environment variable
    3. Default to development
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    config_class = config.get(config_name.lower(), config["default"])
    return config_class()
