from flask import Flask
from app.extensions import db, ckeditor, bootstrap, gravatar, login_manager
from app.routes import auth_bp, main_bp, notes_bp
from app.models import Comment, Note, User # Models importing, so that db.create_all() could see them
from app.api.v1 import api_v1

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Extension initialization
    db.init_app(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)
    gravatar.init_app(app)
    login_manager.init_app(app)

    # Blueprint registration
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(api_v1)

    # IMPORTANT: Import user_loader only after login_manager is ready
    from app.models import user_loader

    # Tables Creation
    with app.app_context():
        db.create_all()

    return app
