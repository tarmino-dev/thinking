import requests

def get_all_notes():
        try:
            response = requests.get(
                url="http://localhost:5000/api/v1/notes")
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error while requesting: {e}")
            return None
        else:
            return response.json()
        
print(get_all_notes())