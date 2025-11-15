import os

class Config:
    SECRET_KEY = os.environ.get('FLASK_KEY')
    GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

    # For GitHub Actions: use in-memory DB automatically
    if os.environ.get("GITHUB_ACTIONS") == "true":
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # For local/production: use environment variable
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')