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

    # ---------- Sidebar / account menu (shared by all logged-in pages) ----------

    @property
    def main_area(self) -> Locator:
        return self.page.get_by_role("main")

    @property
    def account_menu_btn(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"^Account menu"))

    @property
    def account_menu_profile_item(self) -> Locator:
        return self.page.get_by_role("menuitem", name="Profile & Settings")

    @property
    def account_menu(self) -> Locator:
        # התפריט שנפתח מהכפתור: מייל, Profile & Settings, Sign out
        return self.page.get_by_role("menu")

    @property
    def sign_out_item(self) -> Locator:
        return self.page.get_by_role("menuitem", name="Sign out")

    def sidebar_link(self, menu_item: str) -> Locator:
        return self.page.get_by_role("navigation", name="Main").get_by_role("link", name=menu_item, exact=True)

    def page_heading(self, name: str) -> Locator:
        return self.page.get_by_role("heading", level=1, name=name)

    # פותחת את תפריט החשבון (בתחתית הסרגל הצדדי).
    # מחכים קודם שהדף יסיים לטעון: כשהנתונים נטענים הדף מתארך והכפתור זז למטה,
    # ואם התפריט כבר פתוח - הוא נדחף אל מחוץ למסך ואי אפשר ללחוץ עליו.
    def open_account_menu(self) -> None:
        self.page.wait_for_load_state("networkidle")
        self.account_menu_btn.click()

    def sign_out(self) -> None:
        self.open_account_menu()
        self.sign_out_item.click()

    def go_to_profile_from_account_menu(self) -> None:
        self.open_account_menu()
        self.account_menu_profile_item.click()

    def select_option(self, combobox: Locator, option: str) -> None:
        """The site's dropdowns are custom (not <select>): open, then click the option."""
        combobox.click()
        self.page.get_by_role("option", name=option).click()

    # ---------- Login ----------

    def click_sign_in(self) -> None:
        self.sing_in_btn.highlight()
        self.sing_in_btn.click()
    
        
    # def loginAndNavigate(self, enum):
    #     self.login_with_valid_credentials()
    #     self.navigateTo(enum)


    def navigate_to(self, menu_item: str) -> None:
        # Only the sidebar link - the Dashboard also has a "Send money" button
        link = self.sidebar_link(menu_item)
        link.highlight()
        link.click()
        # Verify we landed on the right page
        path = NAV_PAGES_0PTIONS[menu_item]
        expect(self.page).to_have_url(re.compile(re.escape(path) + "$"))
    


    def login_with_valid_credentials(self) -> None:
        self.email_input.fill(EMAIL_YAEL)
        self.password_input.fill(PASSWORD_YAEL)
        self.click_sign_in()
