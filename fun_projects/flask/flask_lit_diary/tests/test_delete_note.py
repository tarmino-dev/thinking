import pytest
from app.models.user import User
from app.models.note import Note
from app.models.comment import Comment
from app.extensions import db


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture
def admin(app):
    # First user inserted gets id=1 — treated as admin.
    user = User(email="admin@test.com", password="hashed", name="Admin")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def user(app, admin):
    u = User(email="user@test.com", password="hashed", name="Regular User")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def other_user(app, admin):
    u = User(email="other@test.com", password="hashed", name="Other User")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def note(app, user):
    n = Note(title="Test Note", subtitle="Sub", body="Body",
             date="June 01, 2026", is_public=True, author=user)
    db.session.add(n)
    db.session.commit()
    return n


# --- Route access ---

def test_delete_note_requires_auth(client, note):
    response = client.get(f"/delete/{note.id}")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_delete_note_not_found(client, user):
    _login(client, user.id)
    response = client.get("/delete/9999")
    assert response.status_code == 404


# --- Ownership ---

def test_delete_own_note_succeeds(client, user, note):
    note_id = note.id
    _login(client, user.id)
    response = client.get(f"/delete/{note_id}")
    assert response.status_code == 302
    assert db.session.get(Note, note_id) is None


def test_delete_note_forbidden_for_non_owner(client, other_user, note):
    _login(client, other_user.id)
    response = client.get(f"/delete/{note.id}")
    assert response.status_code == 403
    assert db.session.get(Note, note.id) is not None


def test_delete_note_allowed_for_admin(client, admin, note):
    note_id = note.id
    _login(client, admin.id)
    response = client.get(f"/delete/{note_id}")
    assert response.status_code == 302
    assert db.session.get(Note, note_id) is None


# --- Cascade ---

def test_delete_note_cascades_to_comments(client, user, note, other_user):
    comment = Comment(text="A comment", comment_author=other_user, parent_note=note)
    db.session.add(comment)
    db.session.commit()
    comment_id = comment.id
    note_id = note.id

    _login(client, user.id)
    client.get(f"/delete/{note_id}")

    assert db.session.get(Comment, comment_id) is None


# --- Redirect ---

def test_delete_note_redirects_to_home(client, user, note):
    _login(client, user.id)
    response = client.get(f"/delete/{note.id}")
    assert response.status_code == 302
    assert "/" in response.headers["Location"]
