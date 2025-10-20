from selenium import webdriver
from selenium.webdriver.common.by import By

URL = "https://www.python.org/"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.get(url=URL)


events_obj = driver.find_elements(by=By.CSS_SELECTOR, value=".event-widget ul")
events = events_obj[0].text.split("\n")

events_data = {i: {"time": events[i * 2], "name": events[i * 2 + 1]}
               for i in range(int(len(events) / 2))}
print(events_data)

# driver.quit()
