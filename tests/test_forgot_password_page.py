import re

from pages.forgot_password_page import ForgotPasswordPage
from playwright.sync_api import Page, expect
import pytest


@pytest.mark.smoke
def test_forgot_password_page_is_displayed(forgot_password_page):
    expect(forgot_password_page.reset_password_title).to_be_visible()
    expect(forgot_password_page.email_input).to_be_visible()
    expect(forgot_password_page.send_reset_link_btn).to_be_visible()
    expect(forgot_password_page.back_to_sign_in_link).to_be_visible()


@pytest.mark.navigation
def test_back_to_sign_in_returns_to_login(forgot_password_page):
    forgot_password_page.click_back_to_sign_in()
    expect(forgot_password_page.page).to_have_url(re.compile(r"/login$"))


# ==================== Positive ====================

@pytest.mark.login
def test_valid_email_shows_confirmation_message(forgot_password_page):
    # A valid-format address that is NOT registered: the site shows the same
    # confirmation message, but no real reset email is sent to our accounts.
    email = "not-registered-user@example.com"
    forgot_password_page.request_reset_link(email)
    expect(forgot_password_page.confirmation_alert).to_be_visible()
    expect(forgot_password_page.confirmation_alert).to_contain_text(email)


# ==================== Negative ====================

@pytest.mark.login
def test_empty_email_shows_error(forgot_password_page):
    forgot_password_page.click_send_reset_link()
    expect(forgot_password_page.email_error).to_be_visible()
    expect(forgot_password_page.email_input).to_have_attribute("aria-invalid", "true")
    expect(forgot_password_page.confirmation_alert).to_be_hidden()


@pytest.mark.login
def test_invalid_email_format_shows_error(forgot_password_page):
    forgot_password_page.request_reset_link("not-an-email")
    expect(forgot_password_page.email_error).to_be_visible()
    expect(forgot_password_page.confirmation_alert).to_be_hidden()
