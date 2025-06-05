import os
import requests
from datetime import datetime

# Fill in the constants with your data.
GENDER = "male" # fill in with yours ("male"/"female")
WEIGHT_KG = 71.5 # fill in with yours (float), kilograms
HEIGHT_CM = 171 # fill in with yours (int), centimeters
AGE = 30 # fill in with yours (int), years

NUTRITIONIX_NUTRIENTS_ENDPOINT = os.environ.get("NUTRITIONIX_NUTRIENTS_ENDPOINT")
NUTRITIONIX_EXERCISE_ENDPOINT = os.environ.get("NUTRITIONIX_EXERCISE_ENDPOINT")
NUTRITIONIX_APP_ID = os.environ.get("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.environ.get("NUTRITIONIX_API_KEY")

SHEETY_ENDPOINT = os.environ.get("SHEETY_ENDPOINT")
SHEETY_TOKEN = os.environ.get("SHEETY_TOKEN")

exercise_text = input("Tell me which exercises you did: ")

nutritionix_headers = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_API_KEY
}

sheety_headers = {
    "Authorization": f"Bearer {SHEETY_TOKEN}"
}

nutritionix_parameters = {
    "query": exercise_text,
    "gender": GENDER,
    "weight_kg": WEIGHT_KG,
    "height_cm": HEIGHT_CM,
    "age": AGE,
}

nutritionix_response = requests.post(url=NUTRITIONIX_EXERCISE_ENDPOINT, json=nutritionix_parameters, headers=nutritionix_headers)
nutritionix_response_json = nutritionix_response.json()

now = datetime.now()
today_date = now.strftime("%d/%m/%Y")
now_time = now.strftime("%H:%M:%S")

for exercise in nutritionix_response_json["exercises"]:
    sheet_inputs = {
        "workout": {
            "date": today_date,
            "time": now_time,
            "exercise": exercise["name"].title(),
            "duration": exercise["duration_min"],
            "calories": exercise["nf_calories"]
        }
    }
    sheety_response = requests.post(url=SHEETY_ENDPOINT, json=sheet_inputs, headers=sheety_headers)
    print(sheety_response.text)
