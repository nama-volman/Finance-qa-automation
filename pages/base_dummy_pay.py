from enum import Enum
import re

from pages.base_page import BasePage
from playwright.sync_api import Locator, Page ,expect
from utilities.config import EMAIL_YAEL, PASSWORD_YAEL
from utilities.navbar_options import NAV_PAGES_0PTIONS

# class NavBar(Enum):
#     dashboard='/'
#     wallets = '/wallats'
#     sendMoney = '/send'

class BaseDummyPayPage(BasePage):
    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page) 

    @property
    def email_input(self) -> Locator:
        return self.page.get_by_role("textbox", name="Email")

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_role("textbox", name="Password")

    @property
    def sing_in_btn(self) -> Locator:
        return self.page.get_by_role("button", name="Sign in")

    def click_sign_in(self) -> None:
        print("----Clicking on Sign in button")
        self.sing_in_btn.highlight()
        self.sing_in_btn.click()
    
        
    # def loginAndNavigate(self, enum):
    #     self.login_with_valid_credentials()
    #     self.navigateTo(enum)


    def navigate_to(self, menu_item: str) -> None:
        link = self.page.get_by_role("link", name=menu_item)
        link.highlight()
        link.click()
        # Verify we landed on the right page
        path = NAV_PAGES_0PTIONS[menu_item]
        expect(self.page).to_have_url(re.compile(re.escape(path) + "$"))
    


    def login_with_valid_credentials(self) -> None:
        self.email_input.fill(EMAIL_YAEL)
        self.password_input.fill(PASSWORD_YAEL)
        self.click_sign_in()
