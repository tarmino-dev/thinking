import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

SHEETY_FLIGHT_DEALS_ENDPOINT = os.getenv("SHEETY_FLIGHT_DEALS_ENDPOINT")
SHEETY_TOKEN = os.getenv("SHEETY_TOKEN")
AMADEUS_TOKEN_ENDPOINT = os.getenv("AMADEUS_TOKEN_ENDPOINT")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
AMADEUS_FLIGHT_OFFERS_SEARCH_ENDPOINT = os.getenv(
    "AMADEUS_FLIGHT_OFFERS_SEARCH_ENDPOINT"
)
AMADEUS_CITY_SEARCH_ENDPOINT = os.getenv("AMADEUS_CITY_SEARCH_ENDPOINT")
