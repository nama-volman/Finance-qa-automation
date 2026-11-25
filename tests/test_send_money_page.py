
import pytest
from playwright.sync_api import expect

from utilities.config import EMAIL_NAAMA


@pytest.mark.positive
@pytest.mark.smoke
def test_send_money_page_is_displayed(send_money_page):
    expect(send_money_page.send_money_title).to_be_visible()
    expect(send_money_page.progress_steps).to_be_visible()
    expect(send_money_page.recipient_email_input).to_be_visible()
    expect(send_money_page.find_recipient_btn).to_be_visible()


@pytest.mark.positive
@pytest.mark.navigation
def test_continue_opens_amount_step_and_back_returns(send_money_page):
    # Only finds the recipient and moves between steps - no money is sent
    send_money_page.find_recipient(EMAIL_NAAMA)
    send_money_page.click_continue()
    expect(send_money_page.send_from_select).to_be_visible()
    expect(send_money_page.amount_input).to_be_visible()
    expect(send_money_page.review_transfer_btn).to_be_visible()

    send_money_page.click_back()
    expect(send_money_page.recipient_email_input).to_be_visible()
    expect(send_money_page.amount_input).to_be_hidden()
