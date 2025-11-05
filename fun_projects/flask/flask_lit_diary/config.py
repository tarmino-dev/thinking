import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.environ.get('FLASK_KEY')
    GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')