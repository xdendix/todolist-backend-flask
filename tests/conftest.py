import pytest
import os
from todo_app import create_app
from todo_app.extensions import db


@pytest.fixture(scope="session")
def app():
    """Create and configure a test app instance."""
    os.environ["SECRET_KEY"] = "test-secret-key"
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def session(app):
    """Create a new database session for a test."""
    with app.app_context():
        db.session.begin_nested()

        yield db.session

        db.session.rollback()
