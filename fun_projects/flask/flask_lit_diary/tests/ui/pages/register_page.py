from selenium.webdriver.common.by import By
from .base_page import BasePage

class RegisterPage(BasePage):
    # Locators
    NAME_INPUT = (By.NAME, "name")
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "input[type='submit']")

    def open_register_page(self):
        self.open("/register")
        return self

    def register(self, name, email, password):
        self.type(self.NAME_INPUT, name)
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)

    def is_logged_in(self):
        """True when the user menu (name dropdown) is visible after auth."""
        return self.is_visible(self.USER_MENU_TOGGLE)
