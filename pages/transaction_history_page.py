import re

from playwright.sync_api import Locator, Page ,expect
from pages.base_dummy_pay import BaseDummyPayPage

class TransactionHistoryPage(BaseDummyPayPage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def history_title(self) -> Locator:
        return self.page_heading("Transaction History")

    # ---------- Filters ----------

    @property
    def from_date_input(self) -> Locator:
        return self.main_area.get_by_role("textbox", name="From date")

    @property
    def to_date_input(self) -> Locator:
        return self.main_area.get_by_role("textbox", name="To date")

    @property
    def type_select(self) -> Locator:
        return self.main_area.get_by_role("combobox", name="Type")

    @property
    def currency_select(self) -> Locator:
        return self.main_area.get_by_role("combobox", name="Currency")

    @property
    def clear_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Clear")

    # ---------- Transactions list ----------

    @property
    def transactions(self) -> Locator:
        return self.main_area.get_by_role("listitem")

    @property
    def first_transaction(self) -> Locator:
        return self.transactions.first.get_by_role("button")

    @property
    def transactions_count_text(self) -> Locator:
        return self.main_area.get_by_text(re.compile(r"^\d+ transactions?$"))

    @property
    def previous_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Previous")

    @property
    def next_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Next")

    @property
    def page_indicator(self) -> Locator:
        return self.main_area.get_by_text(re.compile(r"^Page \d+ of \d+$"))

    @property
    def no_results_text(self) -> Locator:
        return self.main_area.get_by_text("No matching transactions")

    def rows_without_text(self, text: str) -> Locator:
        return self.transactions.filter(has_not_text=text)
    
    # ---------- Transaction details dialog ----------

    @property
    def transaction_dialog(self) -> Locator:
        return self.page.get_by_role("dialog")

    @property
    def dialog_close_btn(self) -> Locator:
        return self.transaction_dialog.get_by_role("button", name="Close")

    # ---------- Actions ----------

    def select_type(self, transaction_type: str) -> None:
        """'All types' / 'Sent' / 'Received'"""
        self.select_option(self.type_select, transaction_type)

    def select_currency(self, currency: str) -> None:
        """'ILS' / 'USD' / 'EUR' / 'GBP'"""
        self.select_option(self.currency_select, currency)

    def click_clear(self) -> None:
        self.clear_btn.click()

    def open_first_transaction(self) -> None:
        # Wait until the list has finished loading (the "N transactions" counter appears)
        self.transactions_count_text.wait_for()
        self.first_transaction.click()

    def close_dialog(self) -> None:
        self.dialog_close_btn.click()

    def click_next(self) -> None:
        self.next_btn.click()

    def click_previous(self) -> None:
        self.previous_btn.click()

    def wait_for_list_loaded(self) -> None:
        self.transactions_count_text.wait_for()

    def set_date_range(self, from_date: str, to_date: str = "") -> None:
        self.from_date_input.fill(from_date)
        self.to_date_input.fill(to_date)
