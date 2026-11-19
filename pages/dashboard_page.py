import re

from playwright.sync_api import Locator, Page ,expect
from pages.base_dummy_pay import BaseDummyPayPage
from utilities.money import parse_amount_to_number

class DashboardPage(BaseDummyPayPage):
    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def dashboard_title(self) -> Locator:
        return self.page.get_by_role("heading", name="Dashboard")

    @property
    def welcome_text(self) -> Locator:
        return self.main_area.get_by_text(re.compile(r"^Welcome back"))

    @property
    def send_money_btn(self) -> Locator:
        return self.main_area.get_by_role("link", name="Send money")

    @property
    def total_balance(self) -> Locator:
        return self.main_area.get_by_text("Total balance").first

    @property
    def your_balances_title(self) -> Locator:
        return self.main_area.get_by_role("heading", name="Your balances")

    @property
    def recent_transactions_title(self) -> Locator:
        return self.main_area.get_by_text("Recent transactions")

    @property
    def view_all_transactions_link(self) -> Locator:
        return self.main_area.locator('a[href="/history"]')

    @property
    def exchange_rates_title(self) -> Locator:
        return self.main_area.get_by_text("Exchange rates")

    @property
    def view_all_notifications_link(self) -> Locator:
        return self.main_area.locator('a[href="/notifications"]')

    # ---------- Total balance card ----------

    @property
    def total_balance_card(self) -> Locator:
        return self.page.get_by_test_id("total-balance")

    @property
    def total_balance_amount(self) -> Locator:
        # "≈ €3,635.99"
        return self.total_balance_card.locator('[data-slot="card-title"]')

    @property
    def total_balance_summary(self) -> Locator:
        # "2 wallets · shown in EUR"
        return self.total_balance_card.locator('[data-slot="card-content"]')

    # ---------- Wallet cards ("Your balances") ----------

    @property
    def wallet_cards(self) -> Locator:
        # data-testid="wallet-ILS", "wallet-EUR", ...
        return self.page.locator('[data-testid^="wallet-"]')

    @property
    def preferred_wallet_card(self) -> Locator:
        return self.wallet_cards.filter(has_text="Preferred")

    # ---------- Exchange rates card ----------

    def rate(self, base: str, target: str) -> Locator:
        # data-testid="rate-EUR-ILS" -> "3.589113"
        return self.page.get_by_test_id(f"rate-{base}-{target}")





    # ---------- Read data (return values, no checks) ----------

    def wait_for_balances_loaded(self) -> None:
        """The page first renders empty cards and fills them a moment later.
        Wait until the summary text and the wallet cards are really there."""
        self.total_balance_summary.filter(has_text="shown in").wait_for()
        self.wallet_cards.first.wait_for()

    def get_total_balance(self) -> float:
        self.wait_for_balances_loaded()
        return parse_amount_to_number(self.total_balance_amount.inner_text())

    def get_preferred_currency(self) -> str:
        # "2 wallets · shown in EUR" -> "EUR"
        self.wait_for_balances_loaded()
        summary = self.total_balance_summary.inner_text()
        return re.search(r"shown in (\w+)", summary).group(1)

    def get_wallet_count_from_summary(self) -> int:
        # "2 wallets · shown in EUR" -> 2
        self.wait_for_balances_loaded()
        summary = self.total_balance_summary.inner_text()
        return int(re.search(r"(\d+) wallets?", summary).group(1))

    def get_wallet_balances(self) -> dict[str, float]:
        """{"ILS": 13000.0, "EUR": 13.93}"""
        self.wait_for_balances_loaded()
        balances = {}
        for card in self.wallet_cards.all():
            currency = card.get_attribute("data-testid").removeprefix("wallet-")
            amount_text = card.locator("p").last.inner_text()   # last <p> = the amount
            balances[currency] = parse_amount_to_number(amount_text)
        return balances

    def get_preferred_wallet_currency(self) -> str:
        """The currency of the wallet marked with the 'Preferred' badge."""
        return self.preferred_wallet_card.get_attribute("data-testid").removeprefix("wallet-")

    def get_rate(self, target: str) -> float:
        """Rate from the preferred currency to `target` (1 EUR -> X ILS)."""
        base = self.get_preferred_currency()
        return float(self.rate(base, target).inner_text())






    # ---------- Actions ----------

    def click_send_money(self) -> None:
        self.send_money_btn.click()

    def click_view_all_transactions(self) -> None:
        self.view_all_transactions_link.click()

    def click_view_all_notifications(self) -> None:
        self.view_all_notifications_link.click()
