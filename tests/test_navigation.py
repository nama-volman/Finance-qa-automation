import re

from playwright.sync_api import expect
import pytest

from utilities.navbar_options import NAV_PAGES_0PTIONS


@pytest.mark.navigation
@pytest.mark.parametrize("menu_item", NAV_PAGES_0PTIONS.keys())
def test_sidebar_link_opens_correct_page(logged_in, menu_item):
    logged_in.navigate_to(menu_item)   # clicks the sidebar link + verifies the URL
    expect(logged_in.page_heading(menu_item)).to_be_visible()


@pytest.mark.navigation
def test_account_menu_opens_profile_settings(logged_in):
    logged_in.go_to_profile_from_account_menu()
    expect(logged_in.page).to_have_url(re.compile(r"/settings$"))
    expect(logged_in.page_heading("Profile & Settings")).to_be_visible()

# Sign-out tests live in tests/test_sign_out.py
