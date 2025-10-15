from flask import Flask
from app.extensions import db
import os
# from app.routes.main import main_bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    # app.config.from_object("config.Config")

    db.init_app(app)

    # app.register_blueprint(main_bp)

    return app
