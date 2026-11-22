
from pages.payment_cards_page import PaymentCardsPage
from pages.login_page import LoginPage
from utilities.config import CARD_DETAILS
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

#positive
@pytest.mark.addCard
def test_add_new_card_with_valid_details(payment_cards_page):
    payment_cards_page.page.pause()
    payment_cards_page.click_add_card()
    expect(payment_cards_page.add_card_dialog).to_be_visible()
    payment_cards_page.fill_card_form(CARD_DETAILS["cardholder_name"],CARD_DETAILS["valid_card_number"],CARD_DETAILS["valid_expiry"],CARD_DETAILS["cvv"])
    payment_cards_page.click_dialog_add()
    expect(payment_cards_page.card_added_toast).to_be_visible()


#negative 
@pytest.mark.addCard
def test_add_new_card_with_invalid_card_number(payment_cards_page):
    payment_cards_page.page.pause()
    payment_cards_page.click_add_card()
    expect(payment_cards_page.add_card_dialog).to_be_visible()
    payment_cards_page.fill_card_form(CARD_DETAILS["cardholder_name"],CARD_DETAILS["invalid_card_number"],CARD_DETAILS["valid_expiry"],CARD_DETAILS["cvv"])
    payment_cards_page.click_dialog_add()
    expect(payment_cards_page.invalid_card_number_message).to_be_visible()
   


#negative 
@pytest.mark.addCard
def test_add_new_card_with_invalid_expiry_date(payment_cards_page):
    payment_cards_page.page.pause()
    payment_cards_page.click_add_card()
    expect(payment_cards_page.add_card_dialog).to_be_visible()
    payment_cards_page.fill_card_form(CARD_DETAILS["cardholder_name"],CARD_DETAILS["valid_card_number"],CARD_DETAILS["invalid_expiry"],CARD_DETAILS["cvv"])
    payment_cards_page.click_dialog_add()
    expect(payment_cards_page.invalid_expiry_date_message).to_be_visible()
   

#positive
# בדיקה: מחיקת כרטיס לפי 3 הפרטים - נשאר כרטיס תואם אחד פחות
@pytest.mark.deleteCard
def test_delete_card(payment_cards_page):
    last4 = CARD_DETAILS["valid_card_number"][-4:]      # "1111"
    holder = CARD_DETAILS["cardholder_name"]            # "Israel Israeli"
    expiry = CARD_DETAILS["valid_expiry"]               # "12/30"

    # Arrange: מחכים שהרשימה תיטען (כרטיסים או "No cards yet"), סופרים, ומוסיפים כרטיס אחד
    expect(payment_cards_page.card_items.first.or_(payment_cards_page.empty_state_text)).to_be_visible()
    cards_before = payment_cards_page.find_card(last4, holder, expiry).count()

    payment_cards_page.click_add_card()
    payment_cards_page.fill_card_form(holder, CARD_DETAILS["valid_card_number"], expiry, CARD_DETAILS["cvv"])
    payment_cards_page.click_dialog_add()
    expect(payment_cards_page.find_card(last4, holder, expiry)).to_have_count(cards_before + 1)   # מחכה שהכרטיס יופיע

    # Act: מוחקים את הכרטיס לפי הפרטים
    payment_cards_page.delete_card(last4, holder, expiry)

    # Assert: מופיעה הודעת "Card removed." וחזרנו למספר שהיה לפני ההוספה
    expect(payment_cards_page.card_removed_toast).to_be_visible()   # קודם ה-toast, לפני שהוא נעלם
    expect(payment_cards_page.find_card(last4, holder, expiry)).to_have_count(cards_before)

# get_by_text("Card number is not valid (")
# def test_delete_card(payment_cards_page):

