import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[3] / '.env'
load_dotenv(dotenv_path=env_path)

PROMISED_MIN_DOWN = os.getenv("PROMISED_MIN_DOWN")
PROMISED_MIN_UP = os.getenv("PROMISED_MIN_UP")
PROMISED_MAX_DOWN = os.getenv("PROMISED_MAX_DOWN")
PROMISED_MAX_UP = os.getenv("PROMISED_MAX_UP")
X_EMAIL = os.getenv("X_EMAIL")
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")
