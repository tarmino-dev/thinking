from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
ckeditor = CKEditor()
bootstrap = Bootstrap5()
gravatar = Gravatar(size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
login_manager = LoginManager()
