import requests
from datetime import datetime
import smtplib
import time

# Fill in the constants with your data.
# Hint: Create an App Password in the Security section of your mailbox' settings
#       and use it instead of your regular password.
MY_EMAIL = ""
MY_PASSWORD = ""
MY_LONG = 13.404954  # Berlin (change to yours)
MY_LAT = 52.520008  # Berlin (change to yours)
MY_TIME_ZONE_ID = "Europe/Berlin"  # Berlin (change to yours)


def is_iss_overhead():
    response = requests.get(
        "http://api.open-notify.org/iss-now.json")  # Endpoint URL
    response.raise_for_status()
    data = response.json()
    iss_longitude = float(data["iss_position"]["longitude"])
    iss_latitude = float(data["iss_position"]["latitude"])
    return MY_LONG - 5 <= iss_longitude <= MY_LONG + 5 and MY_LAT - 5 <= iss_latitude <= MY_LAT + 5


def is_dark():
    time_now = datetime.now().hour
    return not (sunrise <= time_now <= sunset)


def send_notification():
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL,
                            to_addrs=MY_EMAIL,
                            msg="Subject:Look up!\n\nThe ISS is in the sky. Enjoy watching it!")


parameters = {
    "lng": MY_LONG,
    "lat": MY_LAT,
    "formatted": 0,
    "tzid": MY_TIME_ZONE_ID
}

response = requests.get(
    "https://api.sunrise-sunset.org/json", params=parameters)
response.raise_for_status()
data = response.json()
sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

while True:
    time.sleep(60)
    if is_iss_overhead() and is_dark():
        send_notification()
