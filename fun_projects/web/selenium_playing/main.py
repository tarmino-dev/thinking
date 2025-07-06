from selenium import webdriver
from selenium.webdriver.common.by import By

# Keep Chrome browser open after program finishes
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome()
driver.get(
    "https://www.amazon.com/dp/B075CYMYK6?ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6&th=1")

price_dollar = driver.find_element(By.CLASS_NAME, value="a-price-whole")
price_cents = driver.find_element(By.CLASS_NAME, value="a-price-fraction")

print(f"The price is {price_dollar.text}.{price_cents.text}")

# driver.close() # Close the browser tab
driver.quit()  # Close the browser window

driver = webdriver.Chrome()
driver.get("https://www.python.org/")

search_bar = driver.find_element(By.NAME, value="q")
print(search_bar)  # Selenium element
print(search_bar.tag_name)  # Tag name: input
print(search_bar.get_attribute("placeholder"))  # Attribute: Search

button = driver.find_element(By.ID, value="submit")
print(button.size)  # Size of the element: {'height': 40, 'width': 46}

# Finding an "anchor" element in the div with "documentation-widget" class
documentation_link = driver.find_element(
    By.CSS_SELECTOR, value=".documentation-widget a")
print(documentation_link.text)  # docs.python.org

# Using previously copied from browser XPATH
bug_link = driver.find_element(
    By.XPATH, value='//*[@id="site-map"]/div[2]/div/ul/li[3]/a')
print(bug_link.text)  # Submit Website Bug

driver.quit()
