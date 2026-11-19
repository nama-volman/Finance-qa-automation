
from pages.transaction_history_page import TransactionHistoryPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest


@pytest.mark.smoke
def test_transaction_history_page_is_displayed(transaction_history_page):
    expect(transaction_history_page.history_title).to_be_visible()
    expect(transaction_history_page.from_date_input).to_be_visible()
    expect(transaction_history_page.to_date_input).to_be_visible()
    expect(transaction_history_page.type_select).to_be_visible()
    expect(transaction_history_page.currency_select).to_be_visible()
    expect(transaction_history_page.clear_btn).to_be_visible()
    expect(transaction_history_page.previous_btn).to_be_visible()
    expect(transaction_history_page.next_btn).to_be_visible()


@pytest.mark.navigation
def test_click_transaction_opens_details_dialog(transaction_history_page):
    transaction_history_page.open_first_transaction()
    expect(transaction_history_page.transaction_dialog).to_be_visible()

    transaction_history_page.close_dialog()
    expect(transaction_history_page.transaction_dialog).to_be_hidden()
