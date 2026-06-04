from app.models.user import User
from app.models.note import Note
from app.models.comment import Comment
from app.extensions import db
from flask_login import login_user


# --- Auth ---

def test_export_requires_auth(client):
    response = client.get("/api/v1/export")
    assert response.status_code == 401


# --- Profile ---

def test_export_returns_profile(logged_client, user):
    response = logged_client.get("/api/v1/export")
    assert response.status_code == 200

    data = response.get_json()
    profile = data["profile"]
    assert profile["id"] == user.id
    assert profile["email"] == user.email
    assert profile["name"] == user.name
    assert "password" not in profile


# --- Notes ---

def test_export_returns_notes(logged_client, note):
    response = logged_client.get("/api/v1/export")
    data = response.get_json()

    assert len(data["notes"]) == 1
    exported = data["notes"][0]
    assert exported["id"] == note.id
    assert exported["title"] == note.title
    assert exported["body"] == note.body
    assert exported["is_public"] == note.is_public
    assert "author" not in exported


def test_export_excludes_other_users_notes(app, logged_client):
    other = User(email="other@test.com", password="hashed", name="Other")
    db.session.add(other)
    db.session.commit()

    other_note = Note(
        title="Other Note", subtitle="Sub", body="Body",
        date="June 01, 2026", author=other
    )
    db.session.add(other_note)
    db.session.commit()

    response = logged_client.get("/api/v1/export")
    data = response.get_json()

    titles = [n["title"] for n in data["notes"]]
    assert "Other Note" not in titles


# --- Comments ---

def test_export_returns_comments(app, logged_client, user, note):
    comment = Comment(text="My comment", comment_author=user, parent_note=note)
    db.session.add(comment)
    db.session.commit()

    response = logged_client.get("/api/v1/export")
    data = response.get_json()

    assert len(data["comments"]) == 1
    exported = data["comments"][0]
    assert exported["text"] == "My comment"
    assert exported["note_id"] == note.id
    assert exported["note_title"] == note.title


def test_export_excludes_other_users_comments(app, logged_client, note):
    other = User(email="other@test.com", password="hashed", name="Other")
    db.session.add(other)
    db.session.commit()

    other_comment = Comment(text="Other comment", comment_author=other, parent_note=note)
    db.session.add(other_comment)
    db.session.commit()

    response = logged_client.get("/api/v1/export")
    data = response.get_json()

    assert data["comments"] == []
