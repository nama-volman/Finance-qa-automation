import re

from playwright.sync_api import expect
import pytest

from utilities.navbar_options import NAV_PAGES_0PTIONS
from utilities.config import EMAIL_YAEL


@pytest.mark.navigation
@pytest.mark.parametrize("menu_item", NAV_PAGES_0PTIONS.keys())
def test_sidebar_link_opens_correct_page(logged_in, menu_item):
    logged_in.navigate_to(menu_item)   # clicks the sidebar link + verifies the URL
    expect(logged_in.page_heading(menu_item)).to_be_visible()


# בדיקה: לחיצה על כפתור החשבון (בתחתית הסרגל) פותחת תפריט
# עם המייל של המשתמשת, ועם האפשרויות Profile & Settings ו-Sign out
@pytest.mark.navigation
def test_account_menu_opens_with_options(logged_in):
    logged_in.open_account_menu()

    expect(logged_in.account_menu).to_be_visible()
    expect(logged_in.account_menu).to_contain_text(EMAIL_YAEL)
    expect(logged_in.account_menu_profile_item).to_be_visible()
    expect(logged_in.sign_out_item).to_be_visible()


# בדיקה: לחיצה על Profile & Settings בתפריט מעבירה לדף ההגדרות
@pytest.mark.navigation12
def test_account_menu_opens_profile_settings(logged_in):
    logged_in.page.pause()
    logged_in.go_to_profile_from_account_menu()
    expect(logged_in.page).to_have_url(re.compile(r"/settings$"))
    expect(logged_in.page_heading("Profile & Settings")).to_be_visible()

# Sign-out tests live in tests/test_sign_out.py
