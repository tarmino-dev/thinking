import pytest
from app.models import User, Note
from app.extensions import db

def test_create_note(app):
    """Test that a Note can be created and saved to the database."""
    with app.app_context():
        # Create a dummy user to link as the author
        user = User(email="author@example.com", password="testpass", name="Author Name")
        db.session.add(user)
        db.session.commit()

        # Create a new note
        note = Note(
            title="My First Note",
            subtitle="Testing SQLAlchemy relationships",
            date="2025-11-08",
            body="This is the content of the test note.",
            img_url="https://example.com/image.jpg",
            author_id=user.id,
        )

        db.session.add(note)
        db.session.commit()

        # Retrieve from database
        saved_note = Note.query.first()

        assert saved_note is not None
        assert saved_note.title == "My First Note"
        assert saved_note.author.email == "author@example.com"


def test_unique_note_title(app):
    """Test that the title field enforces uniqueness."""
    with app.app_context():
        user = User(email="unique@example.com", password="pw", name="User X")
        db.session.add(user)
        db.session.commit()

        note1 = Note(
            title="Unique Title",
            subtitle="Subtitle 1",
            date="2025-11-08",
            body="First note body",
            img_url="https://example.com/img1.jpg",
            author_id=user.id,
        )
        db.session.add(note1)
        db.session.commit()

        note2 = Note(
            title="Unique Title",  # duplicate title
            subtitle="Subtitle 2",
            date="2025-11-08",
            body="Second note body",
            img_url="https://example.com/img2.jpg",
            author_id=user.id,
        )
        db.session.add(note2)

        # Expect an integrity error on commit
        with pytest.raises(Exception):
            db.session.commit()


def test_note_author_relationship(app):
    """Test that the author relationship works correctly."""
    with app.app_context():
        user = User(email="author2@example.com", password="pw", name="Another Author")
        db.session.add(user)
        db.session.commit()

        note = Note(
            title="Relationship Test",
            subtitle="Testing back_populates",
            date="2025-11-08",
            body="Testing relationships between Note and User.",
            img_url="https://example.com/img.jpg",
            author=user,
        )
        db.session.add(note)
        db.session.commit()

        assert len(user.notes) == 1
        assert user.notes[0].title == "Relationship Test"
