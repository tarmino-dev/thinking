import requests
import os
from twilio.rest import Client

# Fill in the constants with your data.
STOCK = ""
COMPANY_NAME = ""

# ------------------------ALPHAVANTAGE------------------------
ALPHAVANTAGE_ENDPOINT = "https://www.alphavantage.co/query"
ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")
alphavantage_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": ALPHAVANTAGE_API_KEY
}

# ------------------------NEWSAPI------------------------
NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"
NEWSAPI_API_KEY = os.environ.get("NEWSAPI_API_KEY")
newsapi_parameters = {
    "q": COMPANY_NAME,
    "searchIn": "title",
    "apiKey": NEWSAPI_API_KEY
}
ARTICLES_NUMBER = 3

# ------------------------TWILIO------------------------
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
MY_TWILIO_PHONE_NUMBER = ""  # fill in with yours
MY_PHONE_NUMBER = ""  # fill in with yours

# ------------------------------------------------------
response = requests.get(ALPHAVANTAGE_ENDPOINT, params=alphavantage_parameters)
response.raise_for_status()
data = response.json()
dates = list(data["Time Series (Daily)"].keys())
yesterday = dates[0]
DB_yesterday = dates[1]
closing_price_yesterday = float(
    data["Time Series (Daily)"][yesterday]["4. close"])
closing_price_DB_yesterday = float(
    data["Time Series (Daily)"][DB_yesterday]["4. close"])
fluctuation = closing_price_yesterday - closing_price_DB_yesterday
fluctuation_proc = round((fluctuation / closing_price_DB_yesterday) * 100)
fluctuation_sign = None
if fluctuation > 0:
    fluctuation_sign = "🔺"
elif fluctuation < 0:
    fluctuation_sign = "🔻"
if abs(fluctuation) > 0.05 * closing_price_DB_yesterday:
    news_response = requests.get(NEWSAPI_ENDPOINT, params=newsapi_parameters)
    news_response.raise_for_status()
    top_articles = news_response.json()["articles"][:ARTICLES_NUMBER]
    for article in top_articles:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message_text = f"{STOCK}: {fluctuation_sign}{fluctuation_proc}%\nHeadline: {article['title']}\nBrief: {article['description']}"
        message = client.messages.create(
            body=message_text,
            from_=MY_TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER
        )
