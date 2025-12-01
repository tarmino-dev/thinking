from app.models import User
from app.extensions import db

def test_create_user(app):
    """Test creating and retrieving a User."""
    with app.app_context():
        # Create a new user
        user = User(
            email="test@example.com",
            password="secret123",
            name="Test User"
        )
        db.session.add(user)
        db.session.commit()

        # Check that the user is saved in the database
        saved_user = User.query.filter_by(email="test@example.com").first()
        assert saved_user is not None
        assert saved_user.email == "test@example.com"
        assert saved_user.password == "secret123"
        assert saved_user.name == "Test User"

def test_user_relationships(app):
    """Test that user relationships are initially empty."""
    with app.app_context():
        user = User(email="rel@example.com", password="pw", name="RelTest")
        db.session.add(user)
        db.session.commit()

        saved_user = User.query.filter_by(email="rel@example.com").first()
        assert saved_user is not None
        assert isinstance(saved_user.notes, list)
        assert isinstance(saved_user.comments, list)
        assert len(saved_user.notes) == 0
        assert len(saved_user.comments) == 0
