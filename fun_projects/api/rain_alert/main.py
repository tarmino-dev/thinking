# Set the required environment variables before running this script.
# You can export them manually in the terminal, e.g.:
#   export VAR1=value1
#   export VAR2=value2
# Or add them to your shell configuration file (~/.zshrc, ~/.bash_profile, etc.),
# then run 'source ~/.zshrc' (or the appropriate file) to apply the changes.

import requests
from twilio.rest import Client
import os

# Fill in the constants with your data.
MY_LAT = 52.520008  # Berlin (change to yours)
MY_LONG = 13.404954  # Berlin (change to yours)
MY_TWILIO_PHONE_NUMBER = ""  # fill in with yours
MY_PHONE_NUMBER = ""  # fill in with yours
# ---------------------OPENWEATHERMAP-------------------------
OWM_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"
OWM_API_KEY = os.environ.get("OWM_API_KEY")
# If the script is run at 08:00, timestamps 06:00, 09:00, 12:00, 15:00 are going to be picked
TIMESTAMPS_NUMBER = 4
# ---------------------TWILIO SMS SERVICE---------------------
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
# ------------------------------------------------------------
weather_parameters = {
    "lat": MY_LAT,
    "lon": MY_LONG,
    "appid": OWM_API_KEY,
    "cnt": TIMESTAMPS_NUMBER
}
response = requests.get(OWM_ENDPOINT, params=weather_parameters)
response.raise_for_status()
weather_data = response.json()
will_rain = False
for i in range(len(weather_data["list"])):
    if weather_data["list"][i]["weather"][0]["id"] < 700:
        will_rain = True
if will_rain:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body="It's going to rain today. Remember to bring an ☔️",
        from_=MY_TWILIO_PHONE_NUMBER,
        to=MY_PHONE_NUMBER)
    print(message.status)
