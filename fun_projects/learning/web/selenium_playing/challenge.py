from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

URL = "https://secure-retreat-92358.herokuapp.com/"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.get(url=URL)

first_name = driver.find_element(by=By.NAME, value="fName")
first_name.send_keys("My_First_Name")

last_name = driver.find_element(by=By.NAME, value="lName")
last_name.send_keys("My_Last_Name")

email = driver.find_element(by=By.NAME, value="email")
email.send_keys("My_Email@MyEmail")

submit = driver.find_element(by=By.CSS_SELECTOR, value="form button")
submit.click()

# driver.quit()
