import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.environ.get('FLASK_KEY')
    GMAIL_SMTP_ADDRESS = os.environ.get('GMAIL_SMTP_ADDRESS')
    GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL')
    GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')