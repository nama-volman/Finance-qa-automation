
from pages.payment_cards_page import PaymentCardsPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest


@pytest.mark.smoke
def test_payment_cards_page_is_displayed(payment_cards_page):
    expect(payment_cards_page.cards_title).to_be_visible()
    expect(payment_cards_page.add_card_btn).to_be_visible()
    expect(payment_cards_page.simulated_alert).to_be_visible()


@pytest.mark.navigation
def test_add_card_opens_and_cancel_closes_dialog(payment_cards_page):
    payment_cards_page.click_add_card()
    expect(payment_cards_page.add_card_dialog).to_be_visible()
    expect(payment_cards_page.cardholder_name_input).to_be_visible()
    expect(payment_cards_page.card_number_input).to_be_visible()
    expect(payment_cards_page.expiry_input).to_be_visible()
    expect(payment_cards_page.cvv_input).to_be_visible()

    payment_cards_page.cancel_dialog()
    expect(payment_cards_page.add_card_dialog).to_be_hidden()
