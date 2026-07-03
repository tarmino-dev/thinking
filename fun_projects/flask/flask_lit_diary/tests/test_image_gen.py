from app.extensions import db
from app.models import User, Note

ORIGINAL_URL = "https://example.com/original.jpg"


def _make_user_and_note(app):
    """Create an owner, another user, and a note (with an initial img_url)."""
    with app.app_context():
        owner = User(email="owner@example.com", password="hashed", name="Owner")
        other = User(email="other@example.com", password="hashed", name="Other")
        db.session.add_all([owner, other])
        db.session.commit()
        note = Note(
            title="My Note",
            subtitle="Subtitle",
            body="<p>Body</p>",
            is_public=True,
            author=owner,
            date="June 19, 2026",
            img_url=ORIGINAL_URL,
        )
        db.session.add(note)
        db.session.commit()
        return owner.id, other.id, note.id


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _img_url(app, note_id):
    with app.app_context():
        return db.session.get(Note, note_id).img_url


def test_generate_image_requires_auth(client, app):
    _, _, note_id = _make_user_and_note(app)
    response = client.post(f"/note/{note_id}/generate-image")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_generate_image_forbidden_for_non_owner(client, app, monkeypatch):
    _, other_id, note_id = _make_user_and_note(app)
    monkeypatch.setattr("app.images.generate_note_image", lambda note: "nope")
    _login(client, other_id)
    response = client.post(f"/note/{note_id}/generate-image")
    assert response.status_code == 403
    assert _img_url(app, note_id) == ORIGINAL_URL


def test_generate_image_success_updates_img_url(client, app, monkeypatch):
    owner_id, _, note_id = _make_user_and_note(app)
    new_url = f"https://pub-abc.r2.dev/note-images/{note_id}-deadbeef.jpg"
    monkeypatch.setattr("app.images.generate_note_image", lambda note: new_url)

    _login(client, owner_id)
    response = client.post(f"/note/{note_id}/generate-image")
    assert response.status_code == 302
    assert f"/note/{note_id}" in response.headers["Location"]
    assert _img_url(app, note_id) == new_url


def test_generate_image_failure_keeps_img_url(client, app, monkeypatch):
    owner_id, _, note_id = _make_user_and_note(app)

    def boom(note):
        raise RuntimeError("provider down")

    monkeypatch.setattr("app.images.generate_note_image", boom)

    _login(client, owner_id)
    response = client.post(f"/note/{note_id}/generate-image")
    assert response.status_code == 302
    assert f"/note/{note_id}" in response.headers["Location"]
    assert _img_url(app, note_id) == ORIGINAL_URL
