
from playwright.sync_api import Locator, Page ,expect
from pages.base_dummy_pay import BaseDummyPayPage

class BankAccountsPage(BaseDummyPayPage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def bank_accounts_title(self) -> Locator:
        return self.page_heading("Bank Accounts")

    @property
    def add_bank_account_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Add bank account")

    @property
    def simulated_alert(self) -> Locator:
        return self.main_area.get_by_role("alert")

    @property
    def empty_state_text(self) -> Locator:
        return self.main_area.get_by_text("No bank accounts yet")

    # ---------- "Add a simulated bank account" dialog ----------

    @property
    def add_bank_account_dialog(self) -> Locator:
        return self.page.get_by_role("dialog", name="Add a simulated bank account")

    @property
    def holder_name_input(self) -> Locator:
        return self.add_bank_account_dialog.get_by_role("textbox", name="Account holder name")

    @property
    def bank_name_input(self) -> Locator:
        return self.add_bank_account_dialog.get_by_role("textbox", name="Bank name")

    @property
    def country_select(self) -> Locator:
        return self.add_bank_account_dialog.get_by_role("combobox", name="Country")

    @property
    def currency_select(self) -> Locator:
        return self.add_bank_account_dialog.get_by_role("combobox", name="Currency")

    @property
    def account_number_input(self) -> Locator:
        return self.add_bank_account_dialog.get_by_role("textbox", name="IBAN or account number")

    @property
    def dialog_add_btn(self) -> Locator:
        return self.add_bank_account_dialog.get_by_role("button", name="Add bank account")

    @property
    def dialog_cancel_btn(self) -> Locator:
        return self.add_bank_account_dialog.get_by_role("button", name="Cancel")

    @property
    def dialog_close_btn(self) -> Locator:
        return self.add_bank_account_dialog.get_by_role("button", name="Close")

    # ---------- Actions ----------

    def click_add_bank_account(self) -> None:
        self.add_bank_account_btn.click()

    def cancel_dialog(self) -> None:
        self.dialog_cancel_btn.click()

    def fill_bank_account_form(self, holder: str, bank: str, country: str,
                               currency: str, account_number: str) -> None:
        """Fills the form only - does not submit."""
        self.holder_name_input.fill(holder)
        self.bank_name_input.fill(bank)
        self.select_option(self.country_select, country)
        self.select_option(self.currency_select, currency)
        self.account_number_input.fill(account_number)

    def click_dialog_add(self) -> None:
        self.dialog_add_btn.click()
