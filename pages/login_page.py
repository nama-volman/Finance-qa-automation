from playwright.sync_api import Locator, Page, expect

from pages.base_dummy_pay import BaseDummyPayPage
from utilities import config
from utilities.config import EMAIL_YAEL, PASSWORD_YAEL, URL_FINANCE_SITE
import re


class LoginPage(BaseDummyPayPage):
    PATH = URL_FINANCE_SITE

    def __init__(self, page: Page):
        super().__init__(page)

    
    @property
    def login_page_title(self) -> Locator:
        return self.page.get_by_text("DummyPay", exact=True)


    @property
    def forget_password_link(self) -> Locator:
        return self.page.get_by_role("link", name="Forgot password?")
    
    @property
    def dashboard_title(self) -> Locator:
        return self.page.get_by_role("heading", name="Dashboard")



    @property
    def create_account_link(self) -> Locator:
        return self.page.get_by_role("link", name="Create an account")


    # ---------- Validation / error messages ----------

    @property
    def email_error(self) -> Locator:
        return self.page.get_by_text("Enter a valid email address.")

    @property
    def password_error(self) -> Locator:
        return self.page.get_by_text("Enter your password.")

    @property
    def login_error_alert(self) -> Locator:
        """Shown after submitting a wrong email/password combination."""
        return self.page.get_by_role("alert").filter(has_text="Incorrect email or password.")


    def verify_login_page_title(self):
        self.login_page_title.highlight()

    def login(self, email: str, password: str) -> None:
        """Fill the form with any credentials (valid or not) and click Sign in."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.click_sign_in()

    def click_forgot_password(self) -> None:
        self.forget_password_link.click()

    def click_create_account(self) -> None:
        self.create_account_link.click()

