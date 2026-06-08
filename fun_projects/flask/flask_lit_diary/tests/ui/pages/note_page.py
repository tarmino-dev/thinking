from selenium.webdriver.common.by import By
from .base_page import BasePage


class NotePage(BasePage):
    # Locators
    TITLE_INPUT = (By.ID, "title")
    SUBTITLE_INPUT = (By.ID, "subtitle")
    BOOK_INPUT = (By.ID, "note-book-input")
    SUBMIT_BUTTON = (By.ID, "submit")

    def open_new_note_page(self):
        """Open /new-note page using BasePage.open()."""
        self.open("/new-note")
        return self

    def create_note(self, title, subtitle, content, book=None):
        """Fill form fields and CKEditor, then submit."""

        # Title and subtitle (using BasePage.type)
        self.type(self.TITLE_INPUT, title)
        self.type(self.SUBTITLE_INPUT, subtitle)
        if book is not None:
            self.type(self.BOOK_INPUT, book)

        # Set CKEditor content directly — send_keys() on contenteditable is unreliable
        # in headless Chrome and does not update CKEditor's internal data model.
        self.driver.execute_script(
            "CKEDITOR.instances['body'].setData(arguments[0]);"
            "CKEDITOR.instances['body'].updateElement();",
            content
        )

        # Submit the note
        self.js_click(self.SUBMIT_BUTTON)
