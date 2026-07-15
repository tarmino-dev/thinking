import requests
from bs4 import BeautifulSoup
import smtplib
import re
from config import SMTP_ADDRESS, EMAIL, APP_PASSWORD

URL = "https://appbrewery.github.io/instant_pot/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9,uk-UA;q=0.8,uk;q=0.7,de-DE;q=0.6,de;q=0.5,ru-UA;q=0.4,ru;q=0.3,en-US;q=0.2"
}


def main():
    response = requests.get(url=URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find(id="productTitle").get_text().strip()
    # remove whitespace characters (including tabs, line breaks, etc.)
    title = re.sub(r'\s+', ' ', title)
    price = soup.find(class_="a-offscreen").get_text()
    price_without_currency = price.split("$")[1]
    price_as_float = float(price_without_currency)
    if price_as_float < 100:
        message = f"{title} is now {price}"
        with smtplib.SMTP(SMTP_ADDRESS, port=587) as connection:
            connection.starttls()
            connection.login(user=EMAIL, password=APP_PASSWORD)
            connection.sendmail(from_addr=EMAIL,
                                to_addrs=EMAIL,
                                msg=f"Subject:Amazon Price Alert!\n{message}\n{URL}".encode("utf-8"))


if __name__ == "__main__":
    main()
