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


def test_account_page_requires_auth(client):
    response = client.get("/account")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_account_page_loads(client, app):
    with app.app_context():
        user = User(email="acct@example.com", password="hashed", name="Acct User")
        db.session.add(user)
        db.session.commit()
        uid = user.id
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    response = client.get("/account")
    assert response.status_code == 200
    assert b"Account Settings" in response.data


def test_account_page_has_export_link(client, app):
    with app.app_context():
        user = User(email="acct2@example.com", password="hashed", name="Acct User2")
        db.session.add(user)
        db.session.commit()
        uid = user.id
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    response = client.get("/account")
    assert b"/api/v1/export" in response.data


def test_account_page_has_delete_link_for_regular_user(client, app):
    with app.app_context():
        # Insert a placeholder first so the regular user gets id > 1
        placeholder = User(email="admin@placeholder.com", password="hashed", name="Admin")
        db.session.add(placeholder)
        db.session.commit()
        user = User(email="acct3@example.com", password="hashed", name="Acct User3")
        db.session.add(user)
        db.session.commit()
        uid = user.id
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    response = client.get("/account")
    assert b"/delete-account" in response.data


def test_account_page_hides_delete_for_admin(client, app):
    with app.app_context():
        admin = User(email="admin@example.com", password="hashed", name="Admin")
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_id)
        sess["_fresh"] = True
    response = client.get("/account")
    assert response.status_code == 200
    assert b"/delete-account" not in response.data


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
