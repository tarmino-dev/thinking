import requests


class DataManager:
    """This class is responsible for talking to the Google Sheet."""

    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_sheet(self):
        response = requests.get(url=self.endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def put_iata_code(self, row_id, iata_code):
        sheet_inputs = {
            "price": {
                "iataCode": iata_code
            }
        }
        response = requests.put(url=f"{self.endpoint}/{row_id}",
                                json=sheet_inputs,
                                headers=self.headers)
        response.raise_for_status()
        print(response.text)
