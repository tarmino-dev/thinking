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
    # First user inserted on a fresh DB gets id=1 — treated as admin.
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


# --- Route access ---

def test_delete_account_page_requires_auth(client):
    response = client.get("/delete-account")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_delete_account_post_requires_auth(client):
    response = client.post("/delete-account")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_delete_account_page_loads_for_authenticated_user(client, user):
    _login(client, user.id)
    response = client.get("/delete-account")
    assert response.status_code == 200
    assert b"Delete Account" in response.data


def test_delete_account_forbidden_for_admin(client, admin):
    _login(client, admin.id)
    response = client.post("/delete-account")
    assert response.status_code == 403


# --- Deletion and cascade ---

def test_delete_account_removes_user(client, user):
    user_id = user.id
    _login(client, user_id)
    client.post("/delete-account")
    assert db.session.get(User, user_id) is None


def test_delete_account_cascades_to_notes(client, user):
    note = Note(title="My Note", subtitle="Sub", body="Body",
                date="June 01, 2026", author=user)
    db.session.add(note)
    db.session.commit()
    note_id = note.id

    _login(client, user.id)
    client.post("/delete-account")

    assert db.session.get(Note, note_id) is None


def test_delete_account_cascades_to_comments_on_own_notes(client, user, other_user):
    note = Note(title="My Note", subtitle="Sub", body="Body",
                date="June 01, 2026", author=user)
    db.session.add(note)
    db.session.commit()

    comment = Comment(text="A comment", comment_author=other_user, parent_note=note)
    db.session.add(comment)
    db.session.commit()
    comment_id = comment.id

    _login(client, user.id)
    client.post("/delete-account")

    assert db.session.get(Comment, comment_id) is None


def test_delete_account_cascades_to_own_comments_on_others_notes(client, user, other_user):
    note = Note(title="Other Note", subtitle="Sub", body="Body",
                date="June 01, 2026", author=other_user)
    db.session.add(note)
    db.session.commit()

    comment = Comment(text="My comment", comment_author=user, parent_note=note)
    db.session.add(comment)
    db.session.commit()
    comment_id = comment.id

    _login(client, user.id)
    client.post("/delete-account")

    assert db.session.get(Comment, comment_id) is None


def test_delete_account_redirects_to_home(client, user):
    _login(client, user.id)
    response = client.post("/delete-account")
    assert response.status_code == 302
    assert "/" in response.headers["Location"]


def test_delete_account_logs_out_user(client, user):
    _login(client, user.id)
    client.post("/delete-account")
    # Session should no longer grant access to a protected route
    response = client.get("/delete-account")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
