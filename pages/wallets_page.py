import re

from playwright.sync_api import Locator, Page ,expect
from pages.base_dummy_pay import BaseDummyPayPage
from utilities.money import parse_amount_to_number

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

    @property
    def conversion_result(self) -> Locator:
        # "£22.82"
        return self.page.get_by_test_id("conversion-result")

    @property
    def amount_error(self) -> Locator:
        # error under the Amount field, e.g. "Enter a valid positive number."
        return self.page.get_by_test_id("conversion-preview").get_by_role("alert")

    # ---------- Wallet cards ----------

    @property
    def preferred_wallet_card(self) -> Locator:
        # the wallet card with the "Preferred" badge (data-testid="wallet-EUR")
        return self.page.locator('[data-testid^="wallet-"]').filter(has_text="Preferred")

    # ---------- Exchange rates card ----------

    def rate(self, preferred: str, currency: str) -> Locator:
        # data-testid="rate-EUR-ILS" -> "3.672007"  (1 EUR = 3.672007 ILS)
        return self.page.get_by_test_id(f"rate-{preferred}-{currency}")

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

    # ---------- Conversion calculator ----------
    # How the site works: after we type an amount and choose currencies, the site
    # waits a moment, sends a request to the server ("preview_conversion"),
    # and only then shows the result. So we must wait for the server before reading.

    # ממלאת את מחשבון ההמרה (סכום, מטבע מקור, מטבע יעד)
    # ומחכה שתשובת השרת תוצג בדף, כדי שנקרא תוצאה עדכנית.
    def convert(self, amount: float, from_currency: str, to_currency: str) -> None:
        """Fill the calculator and wait until it shows the new result."""

        # Step 1: nothing to change? (e.g. the page's default 100 EUR -> USD)
        #         then the site sends no request, and there is nothing to wait for.
        if self.is_calculator_already_set(amount, from_currency, to_currency):
            return

        # Step 2: fill the calculator, and wait for the server's answer to OUR request
        with self.page.expect_response(
            lambda response: self.is_our_conversion_request(response, amount, from_currency, to_currency)
        ) as response_info:
            self.fill_amount(str(amount))
            self.select_from(from_currency)
            self.select_to(to_currency)

        # Step 3: wait until the page displays the server's answer
        server_answer = response_info.value.json()
        converted = server_answer["receiving_amount_minor"] / 100   # 2282 -> 22.82
        self.wait_until_result_shows(converted)

    def is_calculator_already_set(self, amount: float, from_currency: str, to_currency: str) -> bool:
        """True if the calculator already shows this amount, From and To."""
        self.wait_until_result_has_a_number()   # right after page load the result is empty

        current_amount = float(self.amount_input.input_value())
        current_from = self.from_select.inner_text().strip()
        current_to = self.to_select.inner_text().strip()

        return current_amount == amount and current_from == from_currency and current_to == to_currency

    def is_our_conversion_request(self, response, amount: float, from_currency: str, to_currency: str) -> bool:
        """True if this server response belongs to exactly our amount + currencies.
        (While we fill the form, the site may send requests for in-between states.)"""
        if "preview_conversion" not in response.url:
            return False

        sent = response.request.post_data_json   # what the site sent to the server
        return (sent["p_amount_minor"] == round(amount * 100)   # the site sends cents: 51.20 -> 5120
                and sent["p_from"] == from_currency
                and sent["p_to"] == to_currency)

    def wait_until_result_has_a_number(self) -> None:
        self.conversion_result.filter(has_text=re.compile(r"\d")).wait_for()

    def wait_until_result_shows(self, number: float) -> None:
        """Wait until the result shows this number, e.g. 1204.42 -> "₪1,204.42"."""
        text = f"{number:,.2f}"   # 1204.42 -> "1,204.42"
        # the text must come right after the currency symbol and end the line
        self.conversion_result.filter(has_text=re.compile(rf"\D{re.escape(text)}$")).wait_for()

    # ---------- Read data (return values, no checks) ----------

    # מחזירה את המטבע המועדף מתוך כרטיס הארנק המסומן Preferred: "wallet-EUR" -> "EUR"
    def get_preferred_currency(self) -> str:
        test_id = self.preferred_wallet_card.get_attribute("data-testid")   # "wallet-EUR"
        return test_id.removeprefix("wallet-")                              # "EUR"

    # מחזירה את התוצאה שהמחשבון מציג כמספר: "£22.82" -> 22.82
    def get_converted_amount(self) -> float:
        """The result shown by the calculator, as a number: "£22.82" -> 22.82"""
        return parse_amount_to_number(self.conversion_result.inner_text())

    # קוראת מהדף את השערים מהמטבע המועדף לכל אחד מהמטבעות האחרים
    def get_rates_from(self, preferred: str, currencies: list[str]) -> dict[str, float]:
        """
        Reads the rates from the preferred currency to each of the other currencies:
            get_rates_from("EUR", ["ILS", "USD", "GBP"])
            -> {"ILS": 3.672007, "USD": 1.097333, "GBP": 0.837924}
        """
        rates = {}
        for currency in currencies:
            rates[currency] = float(self.rate(preferred, currency).inner_text())
        return rates
