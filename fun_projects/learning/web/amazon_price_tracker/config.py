import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[3] / '.env'
load_dotenv(dotenv_path=env_path)

SMTP_ADDRESS = os.getenv("GMAIL_SMTP_ADDRESS")
EMAIL = os.getenv("GMAIL_EMAIL")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
