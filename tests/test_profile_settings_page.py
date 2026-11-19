
from pages.profile_settings_page import ProfileSettingsPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest
from utilities.config import EMAIL_YAEL


@pytest.mark.smoke
def test_profile_settings_page_is_displayed(profile_settings_page):
    expect(profile_settings_page.profile_settings_title).to_be_visible()
    expect(profile_settings_page.user_id_value).to_be_visible()
    expect(profile_settings_page.email_value).to_have_text(EMAIL_YAEL)
    expect(profile_settings_page.display_name_input).to_be_visible()
    expect(profile_settings_page.save_btn).to_be_visible()
    expect(profile_settings_page.currency_select).to_be_visible()
    expect(profile_settings_page.change_btn).to_be_visible()
