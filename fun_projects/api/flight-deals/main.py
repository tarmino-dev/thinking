# This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve the program requirements.

import os
import requests
from twilio.rest import Client

SHEETY_FLIGHT_DEALS_ENDPOINT = os.environ.get("SHEETY_FLIGHT_DEALS_ENDPOINT")
SHEETY_TOKEN = os.environ.get("SHEETY_TOKEN")
AMADEUS_TOKEN_ENDPOINT = os.environ.get("AMADEUS_TOKEN_ENDPOINT")
AMADEUS_API_KEY = os.environ.get("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.environ.get("AMADEUS_API_SECRET")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
AMADEUS_FLIGHT_OFFERS_SEARCH_ENDPOINT = os.environ.get(
    "AMADEUS_FLIGHT_OFFERS_SEARCH_ENDPOINT"
)
AMADEUS_CITY_SEARCH_ENDPOINT = os.environ.get("AMADEUS_CITY_SEARCH_ENDPOINT")

sheety_headers = {"Authorization": f"Bearer {SHEETY_TOKEN}"}

amadeus_headers = {"Content-Type": "application/x-www-form-urlencoded"}
amadeus_data = {
    "grant_type": "client_credentials",
    "client_id": AMADEUS_API_KEY,
    "client_secret": AMADEUS_API_SECRET,
}


amadeus_token_response = requests.post(
    url=AMADEUS_TOKEN_ENDPOINT, headers=amadeus_headers, data=amadeus_data
)
amadeus_token_response_json = amadeus_token_response.json()

amadeus_call_headers = {
    "authorization": f"Bearer {amadeus_token_response_json['access_token']}"
}


sheety_cities_response = requests.get(url=SHEETY_FLIGHT_DEALS_ENDPOINT,
                                      headers=sheety_headers)
sheety_cities_response.raise_for_status()
sheety_cities_response_json = sheety_cities_response.json()

for row in sheety_cities_response_json["prices"]:
    city = row["city"].upper()
    row_id = row["id"]
    amadeus_city_search_response = requests.get(url=AMADEUS_CITY_SEARCH_ENDPOINT,
                                                params={
                                                    "keyword": city},
                                                headers=amadeus_call_headers)
    amadeus_city_search_response.raise_for_status()
    amadeus_city_search_response_json = amadeus_city_search_response.json()

    iata_code = amadeus_city_search_response_json["data"][0]["iataCode"]
    sheet_inputs = {
        "price": {
            "iataCode": iata_code
        }
    }
    sheety_iata_code_record_response = requests.put(url=f"{SHEETY_FLIGHT_DEALS_ENDPOINT}/{row_id}",
                                                    json=sheet_inputs,
                                                    headers=sheety_headers)
    sheety_iata_code_record_response.raise_for_status()
    print(sheety_iata_code_record_response.text)


# amadeus_call_response = requests.get(
#     url=AMADEUS_FLIGHT_OFFERS_SEARCH_ENDPOINT,
#     params={
#         "originLocationCode": "SYD",
#         "destinationLocationCode": "BKK",
#         "departureDate": "2025-07-02",
#         "adults": 1,
#     },
#     headers=amadeus_call_headers,
# )
# amadeus_call_response.raise_for_status()
# amadeus_call_response_json = amadeus_call_response.json()
# print(amadeus_call_response_json)
