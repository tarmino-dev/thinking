from app.extensions import db
from app.models import User, Note, Comment


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Literary Diary" in response.data


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data


def test_privacy_page(client):
    response = client.get("/privacy")
    assert response.status_code == 200
    assert b"Privacy" in response.data


def test_contact_page_has_sendgrid_notice(client):
    response = client.get("/contact")
    assert b"SendGrid" in response.data


def test_security_headers_present(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "max-age" in response.headers["Strict-Transport-Security"]


def test_comment_avatar_uses_https_gravatar(app, client):
    with app.app_context():
        user = User(email="commenter@example.com", password="hashed", name="Commenter")
        note = Note(
            title="Note with a comment",
            subtitle="Subtitle",
            date="2026-01-01",
            body="Body",
            is_public=True,
            author=user,
        )
        db.session.add_all([user, note])
        db.session.commit()
        db.session.add(Comment(text="Nice note!", author_id=user.id, note_id=note.id))
        db.session.commit()
        note_id = note.id

    response = client.get(f"/note/{note_id}")
    assert b"https://secure.gravatar.com/avatar/" in response.data
    assert b"http://www.gravatar.com" not in response.data


def test_cookie_banner_present_on_home(client):
    response = client.get("/")
    assert b"cookie-banner" in response.data


def test_cookie_banner_links_to_privacy(client):
    response = client.get("/")
    assert b"/privacy" in response.data


def test_registered_password_uses_16_char_salt(client, app):
    client.post("/register", data={
        "email": "newuser@example.com",
        "password": "SomeStrongPassw0rd!",
        "name": "New User",
    }, follow_redirects=True)

    with app.app_context():
        user = User.query.filter_by(email="newuser@example.com").first()
        method, salt, _ = user.password.split("$", 2)
        assert len(salt) == 16
