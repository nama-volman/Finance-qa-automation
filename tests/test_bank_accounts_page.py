
from pages.bank_accounts_page import BankAccountsPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest
from utilities.config import BANK_ACCOUNT_DETAILS


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


#positive
# בדיקה: הוספת חשבון בנק עם פרטים תקינים - מופיעה הודעת הצלחה והחשבון מופיע ברשימה.
# בסוף הטסט מוחק את החשבון שהוסיף, כדי לא להשאיר חשבונות בדיקה בחשבון.
@pytest.mark.addBankAccount
def test_add_bank_account_with_valid_details(bank_accounts_page):
    details = BANK_ACCOUNT_DETAILS
    bank_name = details["bank_name"]
    last4 = details["valid_account_number"][-4:]          # "5678"
    account = bank_accounts_page.find_bank_account(bank_name, last4)

    # Arrange: מחכים שהרשימה תיטען (חשבונות או "No bank accounts yet"), וסופרים
    expect(bank_accounts_page.bank_account_items.first.or_(bank_accounts_page.empty_state_text)).to_be_visible()
    accounts_before = account.count()

    try:
        # Act: ממלאים את הטופס עם פרטים תקינים ומוסיפים
        bank_accounts_page.add_bank_account(details["holder_name"], bank_name, details["country"],
                                            details["currency"], details["valid_account_number"])

        # Assert: הודעת הצלחה, החלון נסגר, והחשבון החדש מופיע ברשימה
        expect(bank_accounts_page.bank_account_added_toast).to_be_visible()
        expect(bank_accounts_page.add_bank_account_dialog).to_be_hidden()
        expect(account).to_have_count(accounts_before + 1)

    finally:
        # Cleanup: מוחקים את החשבון שהטסט הוסיף (רק אם הוא באמת נוסף)
        if account.count() > accounts_before:
            bank_accounts_page.delete_bank_account(bank_name, last4)
            expect(account).to_have_count(accounts_before)


#negative
# בדיקה: מספר חשבון קצר מ-4 ספרות או ארוך מ-20 ספרות - מופיעה הודעת שגיאה והחשבון לא נוסף
@pytest.mark.addBankAccount
@pytest.mark.parametrize("account_number", 
                         [
    BANK_ACCOUNT_DETAILS["too_short_account_number"],      # 3 ספרות
    BANK_ACCOUNT_DETAILS["too_long_account_number"],       # 21 ספרות
                        ], ids=["too_short", "too_long"])

def test_add_bank_account_with_invalid_account_number(bank_accounts_page, account_number):
    details = BANK_ACCOUNT_DETAILS

    # Act: ממלאים את הטופס עם מספר חשבון לא תקין ומנסים להוסיף
    bank_accounts_page.add_bank_account(details["holder_name"], details["bank_name"], details["country"],
                                        details["currency"], account_number)

    # Assert: הודעת שגיאה, השדה מסומן כלא תקין, והחלון נשאר פתוח (החשבון לא נוסף)
    expect(bank_accounts_page.invalid_account_number_message).to_be_visible()
    expect(bank_accounts_page.account_number_input).to_have_attribute("aria-invalid", "true")
    expect(bank_accounts_page.add_bank_account_dialog).to_be_visible()


#positive
# בדיקה: מחיקת חשבון בנק - מופיעה הודעת "Bank account removed." והחשבון נעלם מהרשימה.
# הטסט מוסיף חשבון בעצמו, כדי שתמיד יהיה מה למחוק, ומוחק אותו - כך החשבון נשאר נקי.
@pytest.mark.deleteBankAccount
def test_delete_bank_account(bank_accounts_page):
    details = BANK_ACCOUNT_DETAILS
    bank_name = details["bank_name"]
    last4 = details["valid_account_number"][-4:]          # "5678"
    account = bank_accounts_page.find_bank_account(bank_name, last4)

    # Arrange: מחכים שהרשימה תיטען, סופרים, ומוסיפים חשבון אחד
    expect(bank_accounts_page.bank_account_items.first.or_(bank_accounts_page.empty_state_text)).to_be_visible()
    accounts_before = account.count()
    bank_accounts_page.add_bank_account(details["holder_name"], bank_name, details["country"],
                                        details["currency"], details["valid_account_number"])
    expect(account).to_have_count(accounts_before + 1)    # מחכים שהחשבון יופיע

    # Act: מוחקים את החשבון
    bank_accounts_page.delete_bank_account(bank_name, last4)

    # Assert: קודם ה-toast (לפני שהוא נעלם), ואז שהחשבון נעלם מהרשימה
    expect(bank_accounts_page.bank_account_removed_toast).to_be_visible()
    expect(account).to_have_count(accounts_before)

