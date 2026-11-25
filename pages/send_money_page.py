import re

from playwright.sync_api import Locator, Page

from pages.base_dummy_pay import BaseDummyPayPage


class SendMoneyPage(BaseDummyPayPage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def send_money_title(self) -> Locator:
        return self.page_heading("Send Money")

    @property
    def progress_steps(self) -> Locator:
        return self.main_area.get_by_role("list", name="Progress")

    # ---------- Step 1: Recipient ----------

    @property
    def recipient_email_input(self) -> Locator:
        return self.main_area.get_by_role("textbox", name="Recipient's email")

    @property
    def find_recipient_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Find recipient")

    @property
    def error_alert(self) -> Locator:
        return self.main_area.get_by_role("alert")

    @property
    def continue_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Continue")

    # ---------- Step 2: Amount ----------

    @property
    def send_from_select(self) -> Locator:
        return self.main_area.get_by_role("combobox", name="Send from")

    @property
    def i_send_radio(self) -> Locator:
        return self.main_area.get_by_role("radio", name="I send")

    @property
    def recipient_gets_radio(self) -> Locator:
        return self.main_area.get_by_role("radio", name="Recipient gets")

    @property
    def amount_input(self) -> Locator:
        # Label includes the currency, e.g. "Amount to send (ILS)"
        return self.main_area.get_by_role("textbox", name=re.compile(r"^Amount to send"))

    @property
    def back_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Back")

    @property
    def review_transfer_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Review transfer")

    # ---------- Actions ----------

    def fill_recipient_email(self, email: str) -> None:
        self.recipient_email_input.fill(email)

    def click_find_recipient(self) -> None:
        self.find_recipient_btn.click()

    def find_recipient(self, email: str) -> None:
        self.fill_recipient_email(email)
        self.click_find_recipient()

    def click_continue(self) -> None:
        self.continue_btn.click()

    def click_back(self) -> None:
        self.back_btn.click()

    def select_send_from(self, wallet: str) -> None:
        self.select_option(self.send_from_select, wallet)

    def fill_amount(self, amount: str) -> None:
        self.amount_input.fill(amount)

    def click_review_transfer(self) -> None:
        self.review_transfer_btn.click()
