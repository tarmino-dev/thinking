from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class BasePage:
    USER_MENU_TOGGLE = (By.ID, "userNavDropdown")
    LOGOUT_LINK = (By.LINK_TEXT, "LOG OUT")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.base_url = base_url

    def open(self, url_path=""):
        self.driver.get(self.base_url + url_path)

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        return element

    def js_click(self, locator):
        element = self.find(locator)
        self.driver.execute_script("arguments[0].click();", element)

    def type(self, locator, text):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def is_visible(self, locator):
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except:
            return False

    def get_text(self, locator):
        return self.find(locator).text

    def logout(self):
        """Open the user menu and click LOG OUT if logged in."""
        if self.is_visible(self.USER_MENU_TOGGLE):
            self.click(self.USER_MENU_TOGGLE)
            self.click(self.LOGOUT_LINK)