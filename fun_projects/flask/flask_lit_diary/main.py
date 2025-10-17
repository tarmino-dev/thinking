from app import create_app
from app.extensions import db
from app.models.user import User

from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager


app = create_app()

# app = Flask(__name__)
ckeditor = CKEditor(app)
Bootstrap5(app)


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# Configure Flask-Login's Login Manager


login_manager = LoginManager()
login_manager.init_app(app)

# Create a user_loader callback


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=False)
