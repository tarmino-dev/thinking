from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import FlightData
from config import *
import datetime
from time import sleep

data_manager = DataManager(
    SHEETY_FLIGHT_DEALS_ENDPOINT, SHEETY_TOKEN)
flight_search = FlightSearch(
    AMADEUS_TOKEN_ENDPOINT, AMADEUS_CITY_SEARCH_ENDPOINT, AMADEUS_FLIGHT_OFFERS_SEARCH_ENDPOINT, AMADEUS_API_KEY, AMADEUS_API_SECRET)

sheet_data = data_manager.get_sheet()
if sheet_data is None:
    print("Failed to receive data. Abort.")
    exit(1)
for row in sheet_data["prices"]:  # Iterating through cities
    if not row["iataCode"]:
        city = row["city"]
        row_id = row["id"]
        iata_code = flight_search.get_destination_code(city.upper())
        data_manager.put_iata_code(row_id, iata_code)
    for days_later in range(1, 4):  # Iterating through dates (3 days starting from tomorrow)
        date = datetime.datetime.now() + datetime.timedelta(days=days_later)
        date_formatted = date.strftime("%Y-%m-%d")
        flight_search_results = flight_search.get_flight_offers(
            row["iataCode"], date_formatted, row["lowestPrice"])
        flight_data = FlightData(flight_search_results)
        data_manager.populate_search_results(
            row['city'],
            flight_data.departure_date,
            flight_data.departure,
            flight_data.arrival,
            flight_data.price,
            flight_data.write)
        sleep(1)
