from selenium.webdriver.common.by import By
from .base_page import BasePage


class NotePage(BasePage):
    # Locators
    TITLE_INPUT = (By.ID, "title")
    SUBTITLE_INPUT = (By.ID, "subtitle")
    SUBMIT_BUTTON = (By.ID, "submit")

    CKEDITOR_IFRAME = (By.CSS_SELECTOR, "iframe.cke_wysiwyg_frame")
    CKEDITOR_BODY = (By.CSS_SELECTOR, "body.cke_editable")

    def open_new_note_page(self):
        """Open /new-note page using BasePage.open()."""
        self.open("/new-note")
        return self

    def create_note(self, title, subtitle, content):
        """Fill form fields and CKEditor, then submit."""

        # Title and subtitle (using BasePage.type)
        self.type(self.TITLE_INPUT, title)
        self.type(self.SUBTITLE_INPUT, subtitle)

        # Switch to CKEditor iframe
        iframe = self.find(self.CKEDITOR_IFRAME)
        self.driver.switch_to.frame(iframe)

        # Type content inside CKEditor body
        body = self.find(self.CKEDITOR_BODY)
        body.send_keys(content)

        # Back to main DOM
        self.driver.switch_to.default_content()

        # Force CKEditor to update underlying textarea
        self.driver.execute_script("""
            for (const instanceName in CKEDITOR.instances) {
                CKEDITOR.instances[instanceName].updateElement();
            }
        """)

        # Debug: check what covers the button
        # submit = self.find(self.SUBMIT_BUTTON)
        # cover = self.driver.execute_script(
        #     "return document.elementFromPoint(arguments[0], arguments[1]);",
        #     submit.location['x'] + submit.size['width'] // 2,
        #     submit.location['y'] + submit.size['height'] // 2
        # )
        # print("Covering element:", cover)

        # Submit the note
        self.js_click(self.SUBMIT_BUTTON)
