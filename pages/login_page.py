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



    def verify_login_page_title(self):               
        self.login_page_title.highlight()

