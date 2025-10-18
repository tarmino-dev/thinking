from flask import Flask
from app.extensions import db, ckeditor, bootstrap, gravatar, login_manager
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.notes import notes_bp

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

    # IMPORTANT: import user_loader after db.init_app and models
    from app.models import user_loader

    # Tables Creation
    with app.app_context():
        db.create_all()

    return app
