import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.note import Note
from flask_login import login_user


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        LOGIN_DISABLED=False,
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    user = User(
        email="test@mail.com",
        password="hashed",
        name="Test User"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def note(app, user):
    note = Note(
        title="Test note",
        subtitle="Subtitle",
        body="Body",
        date="2026-01-01",
        author=user
    )
    db.session.add(note)
    db.session.commit()
    return note


@pytest.fixture
def logged_client(client, user, app):
    with app.test_request_context():
        login_user(user)
    return client
