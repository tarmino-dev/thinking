import requests
import os
from datetime import datetime as dt

# Fill in the constants with your data.
PIXELA_USER = os.environ.get("PIXELA_USER")  # fill in with yours
PIXELA_TOKEN = os.environ.get("PIXELA_TOKEN")  # fill in with yours
PIXELA_ENDPOINT = "https://pixe.la/v1/users"
PIXELA_GRAPH_ID = "graph1"

pixela_parameters = {
    "token": PIXELA_TOKEN,
    "username": PIXELA_USER,
    "agreeTermsOfService": "yes",
    "notMinor": "yes",
}
graph_config = {
    "id": PIXELA_GRAPH_ID,
    "name": "Reading Graph",
    "unit": "pages",
    "type": "int",
    "color": "shibafu"
}
headers = {
    "X-USER-TOKEN": PIXELA_TOKEN
}
pixel_date = dt(year=2025, month=5, day=17)
pixel_date_formatted = pixel_date.strftime("%Y%m%d")
pixel_data_post = {
    "date": pixel_date_formatted,
    "quantity": "24"
}
pixel_data_update = {
    "quantity": "23"
}

# Create a new Pixela user
response = requests.post(url=PIXELA_ENDPOINT, json=pixela_parameters)
print(response.text)

# Create a new pixelation graph definition
response = requests.post(url=f"{PIXELA_ENDPOINT}/{PIXELA_USER}/graphs",
                         json=graph_config, headers=headers)
print(response.text)

# Post a pixel
response = requests.post(
    url=f"{PIXELA_ENDPOINT}/{PIXELA_USER}/graphs/{PIXELA_GRAPH_ID}", json=pixel_data_post, headers=headers)
print(response.text)

# Update a pixel
response = requests.put(
    url=f"{PIXELA_ENDPOINT}/{PIXELA_USER}/graphs/{PIXELA_GRAPH_ID}/{pixel_date_formatted}", json=pixel_data_update, headers=headers)
print(response.text)

# Delete a pixel
response = requests.delete(
    url=f"{PIXELA_ENDPOINT}/{PIXELA_USER}/graphs/{PIXELA_GRAPH_ID}/{pixel_date_formatted}", headers=headers)
print(response.text)
