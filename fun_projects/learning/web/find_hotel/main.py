from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from config import *

URL_ZILLOW = "https://appbrewery.github.io/Zillow-Clone/"
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdB2tNYhGMGzMEL2z0GCc5EtCa4fxeGdGSUPXv27GQWlOLu8Q/viewform?usp=header"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9,uk-UA;q=0.8,uk;q=0.7,de-DE;q=0.6,de;q=0.5,ru-UA;q=0.4,ru;q=0.3,en-US;q=0.2"
}


def main():
    hotel_addresses = []
    hotel_prices = []
    hotel_links = []
    hotel_data = [hotel_addresses, hotel_prices, hotel_links]
    # Get links and addresses
    response = requests.get(url=URL_ZILLOW, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    data_links_addresses = soup.find_all(
        name="a", class_="StyledPropertyCardDataArea-anchor")
    for hotel in data_links_addresses:
        hotel_links.append(hotel.get("href"))
        hotel_addresses.append(hotel.getText().strip().replace(" |", ","))
    # Get prices
    data_prices = soup.find_all(
        name="span", class_="PropertyCardWrapper__StyledPriceLine")
    for hotel in data_prices:
        hotel_price = hotel.getText().strip()
        pattern = r"""
        ^\$             # string starts with "$"
        \d+             # 1 or more digits
        (?:,\d{3})*     # Possible group(s) of "," and 3 digits
        """
        hotel_price_formatted = re.findall(pattern, hotel_price, re.VERBOSE)
        hotel_prices.append(hotel_price_formatted[0])
    # Fill out the forms
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    for num in range(len(hotel_addresses)):
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url=URL_FORM)
        time.sleep(2)
        address_field = driver.find_element(
            by=By.XPATH, value='//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
        price_field = driver.find_element(
            by=By.XPATH, value='//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
        link_field = driver.find_element(
            by=By.XPATH, value='//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
        submit_button = driver.find_element(
            by=By.XPATH, value='//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
        hotel_instance = [hotel[num] for hotel in hotel_data]
        address_field.send_keys(hotel_instance[0])
        price_field.send_keys(hotel_instance[1])
        link_field.send_keys(hotel_instance[2])
        time.sleep(1)
        submit_button.click()
        time.sleep(1)
        driver.quit()


if __name__ == "__main__":
    main()
