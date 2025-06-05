import requests


class DataManager:
    """This class is responsible for talking to the Google Sheet."""

    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_sheet(self):
        try:
            response = requests.get(
                url=f"{self.endpoint}/prices", headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error while requesting: {e}")
            return None
        else:
            return response.json()

    def put_iata_code(self, row_id, iata_code):
        sheet_inputs = {
            "price": {
                "iataCode": iata_code
            }
        }
        response = requests.put(url=f"{self.endpoint}/prices/{row_id}",
                                json=sheet_inputs,
                                headers=self.headers)
        response.raise_for_status()

    def populate_search_results(self, city,	departure_date,	departure_iata_code, arrival_iata_code,	cheapest_price, write):
        if write:
            sheet_inputs = {
                "trip": {
                    "city": city,
                    "departureDate": departure_date,
                    "departureIataCode": departure_iata_code,
                    "arrivalIataCode": arrival_iata_code,
                    "cheapestPrice": cheapest_price
                }
            }
            try:
                response = requests.post(
                    url=f"{self.endpoint}/trips", json=sheet_inputs, headers=self.headers)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"HTTP error: {e}")
                return None
            except requests.exceptions.RequestException as e:
                print(f"Error while requesting: {e}")
                return None
