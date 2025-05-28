# This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve the program requirements.

from data_manager import DataManager
from flight_search import FlightSearch
from twilio.rest import Client
from config import *

data_manager = DataManager(
    SHEETY_FLIGHT_DEALS_ENDPOINT, SHEETY_TOKEN)
flight_search = FlightSearch(
    AMADEUS_TOKEN_ENDPOINT, AMADEUS_CITY_SEARCH_ENDPOINT, AMADEUS_API_KEY, AMADEUS_API_SECRET)

sheet_data = data_manager.get_sheet()["prices"]
for row in sheet_data:
    if not row["iataCode"]:
        city = row["city"]
        row_id = row["id"]
        iata_code = flight_search.get_destination_code(city.upper())
        data_manager.put_iata_code(row_id, iata_code)
