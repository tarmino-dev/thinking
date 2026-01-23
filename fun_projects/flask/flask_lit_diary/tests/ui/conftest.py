import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL of the application under test.
    Change this value depending on your environment.
    """
    return os.getenv("BASE_URL", "http://localhost:5000")  # BASE_URL is pointed in the workflow file for running tests online


@pytest.fixture(scope="session")
def driver():
    """
    Create a Chrome WebDriver instance with headless mode enabled.
    This fixture is session-scoped, so the browser starts once per test session.
    """
    chrome_options = Options()
    # Enable headless mode for CI or automated runs
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    yield driver

    # Quit browser after all tests finish
    driver.quit()


@pytest.fixture
def pages(driver, base_url):
    """
    Provide a small helper object that initializes page objects with driver and base_url.
    This avoids repeating the same constructor calls in every test.
    """
    from .pages.register_page import RegisterPage
    from .pages.login_page import LoginPage
    from .pages.note_page import NotePage

    class Pages:
        register = RegisterPage(driver, base_url)
        login = LoginPage(driver, base_url)
        note = NotePage(driver, base_url)

    return Pages()
