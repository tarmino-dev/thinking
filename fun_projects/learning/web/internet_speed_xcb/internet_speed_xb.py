from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from config import *


class InternetSpeedXBot():
    def __init__(self):
        self.speedtest_url = "https://www.speedtest.net"
        self.x_url = "https://x.com/login"

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(options=self.chrome_options)

        self.down = 0
        self.up = 0

    def get_internet_speed(self):
        # Open speedtest.net website
        self.driver.get(url=self.speedtest_url)
        time.sleep(3)

        # Click "I accept" (Privacy Policy) button
        accept_button = self.driver.find_element(
            by=By.ID, value="onetrust-accept-btn-handler")
        accept_button.click()
        time.sleep(1)

        # Click "Go" button
        go_button = self.driver.find_element(
            by=By.CSS_SELECTOR, value=".start-button a")
        go_button.click()
        time.sleep(60)

        # Get Download and Upload speed
        down_element = self.driver.find_element(
            by=By.CSS_SELECTOR, value=".result-data-large.number.result-data-value.download-speed")
        self.down = float(down_element.text)
        print(self.down)

        up_element = self.driver.find_element(
            by=By.CSS_SELECTOR, value=".result-data-large.number.result-data-value.upload-speed")
        self.up = float(up_element.text)
        print(self.up)

    def tweet_at_provider(self):
        # if self.down < PROMISED_MIN_DOWN or self.up < PROMISED_MIN_UP:

        # Open x.com website
        self.driver.get(url=self.x_url)
        time.sleep(2)

        # Input email
        email_field = self.driver.find_element(
            by=By.XPATH, value='//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')
        email_field.send_keys(X_EMAIL)
        time.sleep(2)
        email_field.send_keys(Keys.ENTER)
        time.sleep(2)

        # Input username
        username_field = self.driver.find_element(by=By.NAME, value='text')
        username_field.send_keys(X_USERNAME)
        time.sleep(2)
        username_field.send_keys(Keys.ENTER)
        time.sleep(2)

        # Input password
        password_field = self.driver.find_element(by=By.NAME, value='password')
        password_field.send_keys(X_PASSWORD)
        time.sleep(2)
        password_field.send_keys(Keys.ENTER)
        time.sleep(10)

        # Build a post message
        message = f"Hey Internet Provider, why is my internet speed {self.down}down/{self.up}up when I pay for {PROMISED_MIN_DOWN}down/{PROMISED_MIN_UP}up?"
        print(message)

        # Input the message into the input field
        input_field = self.driver.find_element(
            by=By.XPATH, value='//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div/div/div/div')
        input_field.send_keys(message)

        # Click the "Post" button
        post_button = self.driver.find_element(
            by=By.XPATH, value='//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/div/button/div/span/span')
        post_button.click()

        print("Posted!")
