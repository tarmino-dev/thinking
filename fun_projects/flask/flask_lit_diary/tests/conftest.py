import os

# Default to an in-memory SQLite database when the environment does not provide
# one. create_app() runs db.create_all() at app-creation time, before the app
# fixture overrides the URI, so a valid URI must exist in the environment by then.
# setdefault never overrides an existing value, so local/CI configs are untouched.
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")

import pytest
from app import create_app, db

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()
