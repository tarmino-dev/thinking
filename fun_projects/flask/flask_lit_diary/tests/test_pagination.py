from app.extensions import db
from app.models import User, Note


def _seed_public_notes(app, count):
    """Create `count` public notes (Note 01..Note NN) authored by one user."""
    with app.app_context():
        user = User(email="author@example.com", password="hashed", name="Author")
        db.session.add(user)
        db.session.commit()
        for i in range(1, count + 1):
            db.session.add(Note(
                title=f"Note {i:02d}",
                subtitle="Subtitle",
                body="Body",
                date="June 19, 2026",
                is_public=True,
                author=user,
            ))
        db.session.commit()


def test_first_page_shows_ten_notes(app, client):
    _seed_public_notes(app, 12)
    response = client.get("/")
    assert response.status_code == 200
    assert response.data.count(b"post-preview") == 10


def test_second_page_shows_remainder(app, client):
    _seed_public_notes(app, 12)
    response = client.get("/?page=2")
    assert response.status_code == 200
    assert response.data.count(b"post-preview") == 2


def test_newest_notes_appear_first(app, client):
    _seed_public_notes(app, 12)
    page1 = client.get("/").data
    page2 = client.get("/?page=2").data
    # Newest (highest id) on page 1, oldest on the last page.
    assert b"Note 12" in page1
    assert b"Note 01" not in page1
    assert b"Note 01" in page2


def test_invalid_page_falls_back_to_first(app, client):
    _seed_public_notes(app, 12)
    expected = client.get("/").data.count(b"post-preview")
    response = client.get("/?page=abc")
    assert response.status_code == 200
    assert response.data.count(b"post-preview") == expected


def test_non_positive_page_falls_back_to_first(app, client):
    _seed_public_notes(app, 12)
    expected = client.get("/").data.count(b"post-preview")
    for value in ("0", "-3"):
        response = client.get(f"/?page={value}")
        assert response.status_code == 200
        assert response.data.count(b"post-preview") == expected


def test_single_page_has_no_pager(app, client):
    _seed_public_notes(app, 3)
    response = client.get("/")
    assert response.status_code == 200
    # Pager links only render when there is more than one page.
    assert b"page=2" not in response.data
