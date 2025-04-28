import requests

response = requests.get("http://api.open-notify.org/iss-now.json") # Endpoint URL
print(response)