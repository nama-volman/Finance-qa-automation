
import pytest
from playwright.sync_api import expect

from utilities.config import HISTORY_FILTERS


@pytest.mark.positive
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


@pytest.mark.positive
@pytest.mark.navigation
def test_click_transaction_opens_details_dialog(transaction_history_page):
    transaction_history_page.open_first_transaction()
    expect(transaction_history_page.transaction_dialog).to_be_visible()

    transaction_history_page.close_dialog()
    expect(transaction_history_page.transaction_dialog).to_be_hidden()

@pytest.mark.negative
@pytest.mark.historyFilters
def test_future_from_date_shows_no_results(transaction_history_page):
    transaction_history_page.wait_for_list_loaded()
    transaction_history_page.set_date_range(HISTORY_FILTERS["future_date"])

    expect(transaction_history_page.no_results_text).to_be_visible()
    expect(transaction_history_page.transactions).to_have_count(0)

@pytest.mark.negative
@pytest.mark.historyFilters
def test_from_after_to_shows_no_results(transaction_history_page):
    transaction_history_page.wait_for_list_loaded()
    transaction_history_page.set_date_range(HISTORY_FILTERS["later_date"],
                                            HISTORY_FILTERS["day_with_two_transactions"])

    expect(transaction_history_page.no_results_text).to_be_visible()
    expect(transaction_history_page.transactions).to_have_count(0)

@pytest.mark.positive
@pytest.mark.historyFilters
def test_filter_by_currency_shows_only_that_currency(transaction_history_page):
    transaction_history_page.wait_for_list_loaded()
    transaction_history_page.select_currency(HISTORY_FILTERS["currency"])

    expect(transaction_history_page.transactions.first).to_be_visible()
    expect(transaction_history_page.rows_without_text(HISTORY_FILTERS["currency_symbol"])).to_have_count(0)

@pytest.mark.positive
@pytest.mark.historyFilters
def test_filter_by_type_shows_only_that_type(transaction_history_page):
    transaction_history_page.wait_for_list_loaded()
    transaction_history_page.select_type(HISTORY_FILTERS["type"])

    expect(transaction_history_page.transactions.first).to_be_visible()
    expect(transaction_history_page.rows_without_text(HISTORY_FILTERS["type"])).to_have_count(0)

@pytest.mark.positive
@pytest.mark.historyFilters
@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="BUG: Clear resets Type but Currency keeps the old value; "
                          "there is also no 'All currencies' option")
def test_clear_resets_all_filters(transaction_history_page):
    transaction_history_page.wait_for_list_loaded()
    transaction_history_page.select_currency(HISTORY_FILTERS["currency"])
    transaction_history_page.select_type(HISTORY_FILTERS["type"])

    transaction_history_page.click_clear()

    expect(transaction_history_page.type_select).to_have_text("All types")
    expect(transaction_history_page.currency_select).to_have_text("All currencies", timeout=5000)

