from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

URL = "https://ozh.github.io/cookieclicker/"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.get(url=URL)

# Wait for language selection to load
time.sleep(2)

# Select English
lang_select = driver.find_element(by=By.ID, value="langSelect-EN")
lang_select.click()

# Wait for game to load
time.sleep(2)

# Click on the Cookie
cookie_button = driver.find_element(by=By.ID, value="bigCookie")
TIMEOUT = time.time() + 5
while True:
    cookie_button.click()
    if time.time() > TIMEOUT:
        break

# driver.quit()
