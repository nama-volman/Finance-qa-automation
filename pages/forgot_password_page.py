
from playwright.sync_api import Locator, Page

from pages.base_dummy_pay import BaseDummyPayPage


class ForgotPasswordPage(BaseDummyPayPage):
    PATH = "/forgot-password"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def reset_password_title(self) -> Locator:
        return self.page.get_by_text("Reset your password")

    @property
    def send_reset_link_btn(self) -> Locator:
        return self.page.get_by_role("button", name="Send reset link")

    @property
    def back_to_sign_in_link(self) -> Locator:
        return self.page.get_by_role("link", name="Back to sign in")

    @property
    def email_error(self) -> Locator:
        return self.page.get_by_text("Enter a valid email address.")

    @property
    def confirmation_alert(self) -> Locator:
        """Shown after a valid email is submitted ("If an account exists for ...")."""
        return self.page.get_by_role("alert").filter(has_text="If an account exists for")

    # email_input is inherited from BaseDummyPayPage (textbox "Email")

    # ---------- Actions ----------

    def fill_email(self, email: str) -> None:
        self.email_input.fill(email)

    def click_send_reset_link(self) -> None:
        self.send_reset_link_btn.click()

    def request_reset_link(self, email: str) -> None:
        self.fill_email(email)
        self.click_send_reset_link()

    def click_back_to_sign_in(self) -> None:
        self.back_to_sign_in_link.click()
