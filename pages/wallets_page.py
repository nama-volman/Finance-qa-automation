
from playwright.sync_api import Locator, Page ,expect
from pages.base_dummy_pay import BaseDummyPayPage

class WalletsPage(BaseDummyPayPage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def wallets_title(self) -> Locator:
        return self.page_heading("Wallets")

    @property
    def add_wallet_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Add wallet")

    @property
    def total_balance(self) -> Locator:
        return self.main_area.get_by_text("Total balance").first

    # ---------- Conversion preview ----------

    @property
    def amount_input(self) -> Locator:
        return self.main_area.get_by_role("textbox", name="Amount")

    @property
    def from_select(self) -> Locator:
        return self.main_area.get_by_role("combobox", name="From")

    @property
    def to_select(self) -> Locator:
        return self.main_area.get_by_role("combobox", name="To")

    @property
    def swap_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Swap")

    @property
    def converted_amount(self) -> Locator:
        return self.main_area.get_by_text("Converted amount")

    # ---------- "Add a currency wallet" dialog ----------

    @property
    def add_wallet_dialog(self) -> Locator:
        return self.page.get_by_role("dialog", name="Add a currency wallet")

    @property
    def dialog_currency_select(self) -> Locator:
        return self.add_wallet_dialog.get_by_role("combobox", name="Currency")

    @property
    def dialog_add_btn(self) -> Locator:
        return self.add_wallet_dialog.get_by_role("button", name="Add wallet")

    @property
    def dialog_cancel_btn(self) -> Locator:
        return self.add_wallet_dialog.get_by_role("button", name="Cancel")

    @property
    def dialog_close_btn(self) -> Locator:
        return self.add_wallet_dialog.get_by_role("button", name="Close")

    # ---------- Actions ----------

    def click_add_wallet(self) -> None:
        self.add_wallet_btn.click()

    def cancel_dialog(self) -> None:
        self.dialog_cancel_btn.click()

    def fill_amount(self, amount: str) -> None:
        self.amount_input.fill(amount)

    def select_from(self, currency: str) -> None:
        self.select_option(self.from_select, currency)

    def select_to(self, currency: str) -> None:
        self.select_option(self.to_select, currency)

    def click_swap(self) -> None:
        self.swap_btn.click()
