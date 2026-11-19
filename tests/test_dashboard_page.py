import re

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest



@pytest.mark.smoke
def test_show_deshbord(dashboard_page):
    dashboard_page.dashboard_title.highlight()
    expect(dashboard_page.dashboard_title).to_be_visible()


@pytest.mark.smoke
def test_dashboard_sections_are_displayed(dashboard_page):
    expect(dashboard_page.welcome_text).to_be_visible()
    expect(dashboard_page.send_money_btn).to_be_visible()
    expect(dashboard_page.total_balance).to_be_visible()
    expect(dashboard_page.your_balances_title).to_be_visible()
    expect(dashboard_page.recent_transactions_title).to_be_visible()
    expect(dashboard_page.exchange_rates_title).to_be_visible()


@pytest.mark.navigation
def test_send_money_button_opens_send_money_page(dashboard_page):
    dashboard_page.click_send_money()
    expect(dashboard_page.page).to_have_url(re.compile(r"/send$"))
    expect(dashboard_page.page_heading("Send Money")).to_be_visible()


@pytest.mark.navigation
def test_view_all_transactions_opens_history_page(dashboard_page):
    dashboard_page.click_view_all_transactions()
    expect(dashboard_page.page).to_have_url(re.compile(r"/history$"))
    expect(dashboard_page.page_heading("Transaction History")).to_be_visible()


@pytest.mark.navigation
def test_view_all_notifications_opens_notifications_page(dashboard_page):
    dashboard_page.click_view_all_notifications()
    expect(dashboard_page.page).to_have_url(re.compile(r"/notifications$"))
    expect(dashboard_page.page_heading("Notifications")).to_be_visible()


# ==================== Total balance ====================

@pytest.mark.dashboard
def test_total_balance_equals_sum_of_wallets(dashboard_page):
    # Arrange - collect the data shown on the page
    preferred = dashboard_page.get_preferred_currency()     # "EUR"
    wallets = dashboard_page.get_wallet_balances()          # {"ILS": 13000.0, "EUR": 13.93}

    # Act - calculate ourselves what the total should be
    expected = 0
    for currency, amount in wallets.items():
        if currency == preferred:
            expected += amount
        else:
            expected += amount / dashboard_page.get_rate(currency)   # e.g. ILS -> EUR

    # Assert - compare to what is displayed (allow 1 cent for rounding)
    actual = dashboard_page.get_total_balance()
    assert actual == pytest.approx(expected, abs=0.01), (
        f"Total balance shown {actual} {preferred}, expected {expected:.2f} "
        f"from wallets {wallets}"
    )


@pytest.mark.dashboard
def test_wallet_count_matches_summary(dashboard_page):
    wallets = dashboard_page.get_wallet_balances()
    assert dashboard_page.get_wallet_count_from_summary() == len(wallets)


@pytest.mark.dashboard
def test_preferred_wallet_matches_summary_currency(dashboard_page):
    dashboard_page.get_wallet_balances()   # wait for the wallets to load
    expect(dashboard_page.preferred_wallet_card).to_have_count(1)
    assert dashboard_page.get_preferred_wallet_currency() == dashboard_page.get_preferred_currency()
