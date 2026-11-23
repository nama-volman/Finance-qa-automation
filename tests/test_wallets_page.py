
from pages.wallets_page import WalletsPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import random
import pytest

from utilities.money import CURRENCIES, convert_with_preferred
from utilities.config import INVALID_AMOUNT_NOT_A_NUMBER, INVALID_AMOUNT_TOO_MANY_DECIMALS


@pytest.mark.smoke
def test_wallets_page_is_displayed(wallets_page):
    expect(wallets_page.wallets_title).to_be_visible()
    expect(wallets_page.add_wallet_btn).to_be_visible()
    expect(wallets_page.total_balance).to_be_visible()
    expect(wallets_page.amount_input).to_be_visible()
    expect(wallets_page.from_select).to_be_visible()
    expect(wallets_page.to_select).to_be_visible()
    expect(wallets_page.swap_btn).to_be_visible()


# מספר הארנקים המקסימלי = ארנק אחד לכל מטבע (4)
MAX_WALLETS = len(CURRENCIES)


# Positive test
# בדיקה: כשיש פחות מ-4 ארנקים, הכפתור לחיץ והחלון נפתח ונסגר.
# אם כבר יש 4 ארנקים - הטסט מדולג (את המצב הזה בודק הטסט השלילי).
@pytest.mark.navigation123
def test_add_wallet_opens_and_cancel_closes_dialog(wallets_page):
    expect(wallets_page.wallet_cards.first).to_be_visible()      # מחכים שהארנקים ייטענו
    if wallets_page.wallet_cards.count() >= MAX_WALLETS:
        pytest.skip("The account already has 4 wallets - Add wallet is disabled")

    expect(wallets_page.add_wallet_btn).to_be_enabled()
    wallets_page.click_add_wallet()
    expect(wallets_page.add_wallet_dialog).to_be_visible()
    expect(wallets_page.dialog_currency_select).to_be_visible()

    wallets_page.cancel_dialog()
    expect(wallets_page.add_wallet_dialog).to_be_hidden()


# Negative test
# בדיקה: כשיש 4 ארנקים (אחד לכל מטבע) - הכפתור Add wallet לא לחיץ.
# אם יש פחות מ-4 ארנקים - הטסט מדולג (את המצב הזה בודק הטסט החיובי).
@pytest.mark.navigation
def test_add_wallet_disabled_when_max_wallets(wallets_page):
    expect(wallets_page.wallet_cards.first).to_be_visible()      # מחכים שהארנקים ייטענו
    if wallets_page.wallet_cards.count() < MAX_WALLETS:
        pytest.skip("The account has less than 4 wallets - Add wallet is enabled")

    expect(wallets_page.add_wallet_btn).to_be_disabled()


# ==================== Conversion calculator ====================
# Only conversions that involve the preferred currency (marked "Preferred" on the Wallets page):
#   preferred -> each of the 3 other currencies   (3 tests)
#   each of the 3 other currencies -> preferred   (3 tests)

# השלבים המשותפים לשני הכיוונים: קוראת שערים, ממירה סכום אקראי במחשבון,
# ומשווה את התוצאה באתר לחישוב שלנו (סטייה של עד סנט)
def check_conversion(wallets_page, preferred, from_currency, to_currency):
    """Shared steps for both directions."""
    # Arrange - read the rates from the preferred currency, pick a random amount
    other_currencies = [c for c in CURRENCIES if c != preferred]
    rates = wallets_page.get_rates_from(preferred, other_currencies)
    amount = round(random.uniform(1, 1000), 2)   # e.g. 437.82

    # Act - convert with the site's calculator
    wallets_page.convert(amount, from_currency, to_currency)

    # Assert - the site's result equals our own calculation (allow 1 cent for rounding)
    expected = convert_with_preferred(amount, from_currency, to_currency, preferred, rates)
    actual = wallets_page.get_converted_amount()
    assert actual == pytest.approx(expected, abs=0.01), (
        f"{amount} {from_currency} -> {to_currency}: site shows {actual}, "
        f"expected {expected:.2f} (preferred {preferred}, rates {rates})"
    )


# בדיקה: המרה מהמטבע המועדף לכל אחד מ-3 המטבעות האחרים
@pytest.mark.wallets
@pytest.mark.parametrize("other_currency", CURRENCIES)
def test_convert_from_preferred_currency(wallets_page, other_currency):
    preferred = wallets_page.get_preferred_currency()
    if other_currency == preferred:
        pytest.skip(f"{other_currency} is the preferred currency")
    check_conversion(wallets_page, preferred, preferred, other_currency)


# בדיקה: המרה מכל אחד מ-3 המטבעות האחרים אל המטבע המועדף
@pytest.mark.wallets
@pytest.mark.parametrize("other_currency", CURRENCIES)
def test_convert_to_preferred_currency(wallets_page, other_currency):
    preferred = wallets_page.get_preferred_currency()
    if other_currency == preferred:
        pytest.skip(f"{other_currency} is the preferred currency")
    check_conversion(wallets_page, preferred, other_currency, preferred)


# ==================== Conversion calculator - negative ====================

# בדיקה שלילית: הכנסת ערך שאינו מספר (אותיות) - מופיעה הודעת שגיאה ואין תוצאה
@pytest.mark.wallets
def test_amount_not_a_number_shows_error(wallets_page):
    wallets_page.fill_amount(INVALID_AMOUNT_NOT_A_NUMBER)

    expect(wallets_page.amount_error).to_have_text("Enter a valid positive number.")
    expect(wallets_page.amount_input).to_have_attribute("aria-invalid", "true")
    expect(wallets_page.conversion_result).to_have_text("—")


# בדיקה שלילית: מספר עם יותר מ-2 ספרות אחרי הנקודה - מופיעה הודעת שגיאה ואין תוצאה
@pytest.mark.wallets
def test_amount_with_more_than_2_decimals_shows_error(wallets_page):
    wallets_page.fill_amount(INVALID_AMOUNT_TOO_MANY_DECIMALS)

    expect(wallets_page.amount_error).to_have_text("Use at most 2 decimal places.")
    expect(wallets_page.amount_input).to_have_attribute("aria-invalid", "true")
    expect(wallets_page.conversion_result).to_have_text("—")
