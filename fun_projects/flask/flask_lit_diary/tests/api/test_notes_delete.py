from app.models.note import Note
from app.models.user import User
from app.extensions import db
from flask_login import login_user

# Successful Deletion (204)
def test_delete_note_success(logged_client, note):
    response = logged_client.delete(f"/api/v1/notes/{note.id}")

    assert response.status_code == 204

    # Check that the note has actually been deleted from the database
    deleted_note = Note.query.get(note.id)
    assert deleted_note is None

# Unauthorized (401)
def test_delete_note_unauthorized(client, note):
    response = client.delete(f"/api/v1/notes/{note.id}")

    assert response.status_code == 401

# Someone else's Note (403)
def test_delete_note_forbidden(client, app, note):
    other_user = User(
        email="other@mail.com",
        password="hashed",
        name="Other User"
    )
    db.session.add(other_user)
    db.session.commit()

    with app.test_request_context():
        login_user(other_user)

    response = client.delete(f"/api/v1/notes/{note.id}")

    assert response.status_code == 403

# Note not found (404)
def test_delete_note_not_found(logged_client):
    response = logged_client.delete("/api/v1/notes/9999")

    assert response.status_code == 404
