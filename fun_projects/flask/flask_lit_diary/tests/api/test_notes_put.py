from app.models.user import User
from app.extensions import db

# Successful Update (200)
def test_update_note_success(logged_client, note):
    response = logged_client.put(
        f"/api/v1/notes/{note.id}",
        json={
            "title": "Updated title",
            "body": "Updated body"
        }
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["title"] == "Updated title"
    assert data["body"] == "Updated body"

# Unauthorized (401)
def test_update_note_unauthorized(client, note):
    response = client.put(
        f"/api/v1/notes/{note.id}",
        json={"title": "Hack"}
    )

    assert response.status_code == 401

# Someone else's Note (403)
def test_update_note_forbidden(client, app, note):
    other_user = User(
        email="other@mail.com",
        password="hashed",
        name="Other"
    )
    db.session.add(other_user)
    db.session.commit()

    with app.test_request_context():
        from flask_login import login_user
        login_user(other_user)

    response = client.put(
        f"/api/v1/notes/{note.id}",
        json={"title": "Hack"}
    )

    assert response.status_code == 403

# Note not found (404)
def test_update_note_not_found(logged_client):
    response = logged_client.put(
        "/api/v1/notes/9999",
        json={"title": "Nope"}
    )

    assert response.status_code == 404

# Invalid JSON (400)
def test_update_note_invalid_json(logged_client, note):
    response = logged_client.put(
        f"/api/v1/notes/{note.id}",
        data="not-json",
        content_type="application/json"
    )

    assert response.status_code == 400
