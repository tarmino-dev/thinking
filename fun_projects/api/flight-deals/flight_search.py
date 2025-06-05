import requests


class FlightSearch:
    """This class is responsible for talking to the Flight Search API."""

    def __init__(self, token_endpoint, city_search_endpoint, flight_offers_search_endpoint, api_key, api_secret):
        self.token_endpoint = token_endpoint
        self.city_search_endpoint = city_search_endpoint
        self.flight_offers_search_endpoint = flight_offers_search_endpoint
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {"authorization": f"Bearer {self.get_token()}"}

    def get_token(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret,
        }
        response = requests.post(
            url=self.token_endpoint, headers=headers, data=data
        )
        response.raise_for_status()
        token = response.json()['access_token']
        return token

    def get_destination_code(self, city_name):
        response = requests.get(url=self.city_search_endpoint,
                                params={
                                    "keyword": city_name},
                                headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        iata_code = response_json["data"][0]["iataCode"]
        return iata_code

    def get_flight_offers(self, destination_location_code, departure_date, max_price):
        parameters = {
            "originLocationCode": "FRA",
            "destinationLocationCode": destination_location_code,
            "departureDate": departure_date,
            "adults": 1,
            "nonStop": "true",
            "currencyCode": "EUR",
            "maxPrice": max_price
        }
        response = requests.get(url=self.flight_offers_search_endpoint,
                                params=parameters,
                                headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        return response_json
