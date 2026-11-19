
from pages.wallets_page import WalletsPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest


@pytest.mark.smoke
def test_wallets_page_is_displayed(wallets_page):
    expect(wallets_page.wallets_title).to_be_visible()
    expect(wallets_page.add_wallet_btn).to_be_visible()
    expect(wallets_page.total_balance).to_be_visible()
    expect(wallets_page.amount_input).to_be_visible()
    expect(wallets_page.from_select).to_be_visible()
    expect(wallets_page.to_select).to_be_visible()
    expect(wallets_page.swap_btn).to_be_visible()


@pytest.mark.navigation
def test_add_wallet_opens_and_cancel_closes_dialog(wallets_page):
    wallets_page.click_add_wallet()
    expect(wallets_page.add_wallet_dialog).to_be_visible()
    expect(wallets_page.dialog_currency_select).to_be_visible()

    wallets_page.cancel_dialog()
    expect(wallets_page.add_wallet_dialog).to_be_hidden()
