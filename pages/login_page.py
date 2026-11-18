from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utilities import config
from utilities.config import URL_FINANCE_SITE
import re


class LoginPage(BasePage):
    PATH = URL_FINANCE_SITE

    def __init__(self, page: Page):
        super().__init__(page)


    @property
    def logIn(self) -> Locator:
        #return self.page.get_by_role("link", name="Sign in")
        return True

    def clickLogIn(self) -> None:
        print("Clickin on Log In button")
        self.logIn.click()
        # self.page.wait_for_url("**/login")