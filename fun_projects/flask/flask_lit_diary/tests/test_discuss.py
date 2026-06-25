from app.extensions import db
from app.models import User, Note


def _make_user_and_note(app, public=True):
    """Create an owner, another user, and a note authored by the owner."""
    with app.app_context():
        owner = User(email="owner@example.com", password="hashed", name="Owner")
        other = User(email="other@example.com", password="hashed", name="Other")
        db.session.add_all([owner, other])
        db.session.commit()
        note = Note(
            title="My Note",
            subtitle="Subtitle",
            body="<p>Body</p>",
            is_public=public,
            author=owner,
            date="June 19, 2026",
        )
        db.session.add(note)
        db.session.commit()
        return owner.id, other.id, note.id


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


# --- discussion page (GET) ---

def test_discuss_page_requires_auth(client, app):
    _, _, note_id = _make_user_and_note(app)
    response = client.get(f"/note/{note_id}/discuss")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_discuss_page_loads_for_owner(client, app):
    owner_id, _, note_id = _make_user_and_note(app)
    _login(client, owner_id)
    response = client.get(f"/note/{note_id}/discuss")
    assert response.status_code == 200
    assert b"discuss" in response.data.lower()


def test_discuss_page_forbidden_for_non_owner(client, app):
    _, other_id, note_id = _make_user_and_note(app)
    _login(client, other_id)
    response = client.get(f"/note/{note_id}/discuss")
    assert response.status_code == 403


# --- discussion message (POST) ---

def test_discuss_message_returns_reply(client, app, monkeypatch):
    owner_id, _, note_id = _make_user_and_note(app)
    captured = {}

    def fake_discuss(note, history):
        captured["history"] = history
        return "AI reply"

    monkeypatch.setattr("app.ai.discuss_note", fake_discuss)

    _login(client, owner_id)
    response = client.post(
        f"/note/{note_id}/discuss",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert response.status_code == 200
    assert response.get_json() == {"reply": "AI reply"}
    assert captured["history"] == [{"role": "user", "content": "Hello"}]


def test_discuss_message_forbidden_for_non_owner(client, app, monkeypatch):
    _, other_id, note_id = _make_user_and_note(app)
    monkeypatch.setattr("app.ai.discuss_note", lambda note, history: "should not run")
    _login(client, other_id)
    response = client.post(
        f"/note/{note_id}/discuss",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert response.status_code == 403


def test_discuss_message_requires_auth(client, app):
    _, _, note_id = _make_user_and_note(app)
    response = client.post(
        f"/note/{note_id}/discuss",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_discuss_message_rejects_empty_history(client, app):
    owner_id, _, note_id = _make_user_and_note(app)
    _login(client, owner_id)
    response = client.post(f"/note/{note_id}/discuss", json={"messages": []})
    assert response.status_code == 400


def test_discuss_message_rejects_non_user_last_turn(client, app):
    owner_id, _, note_id = _make_user_and_note(app)
    _login(client, owner_id)
    response = client.post(
        f"/note/{note_id}/discuss",
        json={"messages": [{"role": "assistant", "content": "Hi"}]},
    )
    assert response.status_code == 400
