
from pages.bank_accounts_page import BankAccountsPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest


@pytest.mark.smoke
def test_bank_accounts_page_is_displayed(bank_accounts_page):
    expect(bank_accounts_page.bank_accounts_title).to_be_visible()
    expect(bank_accounts_page.add_bank_account_btn).to_be_visible()
    expect(bank_accounts_page.simulated_alert).to_be_visible()


@pytest.mark.navigation
def test_add_bank_account_opens_and_cancel_closes_dialog(bank_accounts_page):
    bank_accounts_page.click_add_bank_account()
    expect(bank_accounts_page.add_bank_account_dialog).to_be_visible()
    expect(bank_accounts_page.holder_name_input).to_be_visible()
    expect(bank_accounts_page.bank_name_input).to_be_visible()
    expect(bank_accounts_page.country_select).to_be_visible()
    expect(bank_accounts_page.currency_select).to_be_visible()
    expect(bank_accounts_page.account_number_input).to_be_visible()

    bank_accounts_page.cancel_dialog()
    expect(bank_accounts_page.add_bank_account_dialog).to_be_hidden()
