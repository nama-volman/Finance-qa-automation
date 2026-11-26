import random
from datetime import datetime

import pytest
from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage
from utilities import navbar_options as navbar
from utilities.config import EMAIL_YAEL, PROFILE_DETAILS
from utilities.money import CURRENCIES


@pytest.mark.positive
@pytest.mark.smoke
def test_profile_settings_page_is_displayed(profile_settings_page):
    expect(profile_settings_page.profile_settings_title).to_be_visible()
    expect(profile_settings_page.user_id_value).to_be_visible()
    expect(profile_settings_page.email_value).to_have_text(EMAIL_YAEL)
    expect(profile_settings_page.display_name_input).to_be_visible()
    expect(profile_settings_page.save_btn).to_be_visible()
    expect(profile_settings_page.currency_select).to_be_visible()
    expect(profile_settings_page.change_btn).to_be_visible()


# בדיקה: מילוי שם תקין - מופיעה הודעת הצלחה והשם החדש מוצג בפרופיל.
# מוסיפים לשם את השעה (עם שניות), כי כפתור Save לא פעיל כשהשם לא השתנה מההרצה הקודמת.
# שעה תמיד שונה מההרצה הקודמת, בניגוד למספר אקראי שיכול לחזור על עצמו.
@pytest.mark.positive
@pytest.mark.profile
def test_change_display_name_valid(profile_settings_page):
    new_name = f"{PROFILE_DETAILS['valid_display_name']} {datetime.now().strftime('%H%M%S')}"   # "QA Tester 143025"
    profile_settings_page.change_display_name(new_name)

    expect(profile_settings_page.display_name_updated_toast).to_be_visible()
    expect(profile_settings_page.display_name_value).to_have_text(new_name)


# בדיקה: מילוי שם קצר מ-2 תווים או ארוך מ-50 תווים - מופיעה הודעת שגיאה
@pytest.mark.negative
@pytest.mark.profile
@pytest.mark.parametrize("invalid_name, error_message", [
    (PROFILE_DETAILS["too_short_display_name"], "Display name must be at least 2 characters."),
    (PROFILE_DETAILS["too_long_display_name"], "Display name must be at most 50 characters."),
], ids=["too_short", "too_long"])
def test_change_display_name_invalid(profile_settings_page, invalid_name, error_message):
    profile_settings_page.change_display_name(invalid_name)

    expect(profile_settings_page.display_name_error).to_have_text(error_message)


# בדיקה: בחירת מטבע מועדף אחר (מוגרל מבין 3 המטבעות שאינם מועדפים כרגע).
# אחרי השינוי עוברים לדשבורד ומוודאים שהסכום הכולל מוצג במטבע החדש ("shown in GBP").
@pytest.mark.positive
@pytest.mark.profile
def test_change_preferred_currency(profile_settings_page):
    current_currency = profile_settings_page.get_preferred_currency()                      # "USD"
    new_currency = random.choice([c for c in CURRENCIES if c != current_currency])        # למשל "GBP"
    profile_settings_page.change_preferred_currency(new_currency)
    expect(profile_settings_page.currency_changed_toast(new_currency)).to_be_visible()

    profile_settings_page.navigate_to(navbar.DASHBOARD)
    dashboard_page = DashboardPage(profile_settings_page.page)
    expect(dashboard_page.total_balance_summary).to_contain_text(f"shown in {new_currency}")
