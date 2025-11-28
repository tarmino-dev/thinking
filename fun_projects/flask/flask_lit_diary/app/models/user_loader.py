from app.extensions import db
from app.models.user import User
from app.extensions import login_manager


# Configure Flask-Login's Login Manager: Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)