import pytest
from app.models import User, Note, Comment
from app.extensions import db

def test_create_comment(app):
    """Test that a Comment can be created and linked to a Note and User."""
    with app.app_context():
        user = User(email="commenter@example.com", password="pw", name="Commenter")
        note = Note(
            title="Commented Note",
            subtitle="Subtitle",
            date="2025-11-08",
            body="Note body for comment test.",
            img_url="https://example.com/note.jpg",
            author=user,
        )
        db.session.add_all([user, note])
        db.session.commit()

        comment = Comment(
            text="This is a test comment.",
            author_id=user.id,
            note_id=note.id,
        )
        db.session.add(comment)
        db.session.commit()

        saved_comment = Comment.query.first()

        assert saved_comment is not None
        assert saved_comment.text == "This is a test comment."
        assert saved_comment.comment_author.email == "commenter@example.com"
        assert saved_comment.parent_note.title == "Commented Note"


def test_comment_relationships(app):
    """Test bidirectional relationships between Comment, User, and Note."""
    with app.app_context():
        user = User(email="rel@example.com", password="pw", name="RelTester")
        note = Note(
            title="Note for relationships",
            subtitle="Sub",
            date="2025-11-08",
            body="Body text",
            img_url="https://example.com/image.jpg",
            author=user,
        )
        db.session.add_all([user, note])
        db.session.commit()

        comment1 = Comment(text="First comment", author_id=user.id, note_id=note.id)
        comment2 = Comment(text="Second comment", author_id=user.id, note_id=note.id)
        db.session.add_all([comment1, comment2])
        db.session.commit()

        assert len(note.comments) == 2
        assert note.comments[0].text == "First comment"
        assert note.comments[1].text == "Second comment"
        assert len(user.comments) == 2


def test_comment_without_author_or_note(app):
    """Test that Comment cannot exist without both author and note."""
    with app.app_context():
        comment = Comment(text="Orphan comment", author_id=None, note_id=None)
        db.session.add(comment)
        with pytest.raises(Exception):
            db.session.commit()
