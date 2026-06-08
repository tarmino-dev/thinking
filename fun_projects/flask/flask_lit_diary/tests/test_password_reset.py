from unittest.mock import patch
from werkzeug.security import check_password_hash
from app.models.user import User
from app.extensions import db
from app.routes.auth import _generate_reset_token


def _seed_user(app):
    with app.app_context():
        user = User(
            email="user@example.com",
            password="pbkdf2:sha256:600000$somesalt1234567$" + "a" * 64,
            name="Test User",
        )
        db.session.add(user)
        db.session.commit()
        return user.id


def test_forgot_password_page_loads(client):
    response = client.get("/forgot-password")
    assert response.status_code == 200
    assert b"Forgot Password" in response.data


def test_forgot_password_unknown_email_redirects(client):
    response = client.post("/forgot-password", data={"email": "nobody@example.com"}, follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_forgot_password_always_shows_generic_message(client):
    response = client.post("/forgot-password", data={"email": "nobody@example.com"}, follow_redirects=True)
    assert b"reset link" in response.data


def test_forgot_password_known_email_sends_email(app, client):
    _seed_user(app)
    with patch("app.routes.auth.send_email") as mock_send:
        mock_send.return_value = True
        client.post("/forgot-password", data={"email": "user@example.com"})
        mock_send.assert_called_once()
        _, kwargs = mock_send.call_args
        assert kwargs.get("to_email") == "user@example.com" or mock_send.call_args[0][2] == "user@example.com"


def test_reset_password_invalid_token_redirects(client):
    response = client.get("/reset-password/invalidtoken", follow_redirects=False)
    assert response.status_code == 302
    assert "forgot-password" in response.headers["Location"]


def test_reset_password_valid_token_loads_form(app, client):
    _seed_user(app)
    with app.app_context():
        token = _generate_reset_token("user@example.com")
    response = client.get(f"/reset-password/{token}")
    assert response.status_code == 200
    assert b"Reset Password" in response.data


def test_reset_password_updates_password(app, client):
    user_id = _seed_user(app)
    with app.app_context():
        token = _generate_reset_token("user@example.com")
    client.post(f"/reset-password/{token}", data={
        "password": "NewSecurePass1!",
        "confirm": "NewSecurePass1!",
    })
    with app.app_context():
        user = db.session.get(User, user_id)
        assert check_password_hash(user.password, "NewSecurePass1!")


def test_reset_password_redirects_to_login(app, client):
    _seed_user(app)
    with app.app_context():
        token = _generate_reset_token("user@example.com")
    response = client.post(f"/reset-password/{token}", data={
        "password": "NewSecurePass1!",
        "confirm": "NewSecurePass1!",
    }, follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
