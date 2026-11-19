
import re

from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest
from utilities.config import URL_FINANCE_SITE, EMAIL_YAEL, PASSWORD_YAEL, EMAIL_NAAMA, PASSWORD_NAAMA


@pytest.mark.smoke
def test_login_to_finance_site(page: Page):
    loginPage = LoginPage(page)
    loginPage.open()

    loginPage.verify_login_page_title()  # בדיקה שהכותרת של הדף היא DummyPay
    expect(loginPage.login_page_title).to_be_visible()

    loginPage.login_with_valid_credentials()
    expect(loginPage.page).to_have_url(URL_FINANCE_SITE)
    expect(loginPage.dashboard_title).to_be_visible()


@pytest.mark.smoke
def test_login_page_elements_are_displayed(login_page):
    expect(login_page.login_page_title).to_be_visible()
    expect(login_page.email_input).to_be_visible()
    expect(login_page.password_input).to_be_visible()
    expect(login_page.sing_in_btn).to_be_visible()
    expect(login_page.forget_password_link).to_be_visible()
    expect(login_page.create_account_link).to_be_visible()


@pytest.mark.navigation
def test_forgot_password_link_opens_forgot_password_page(login_page):
    login_page.click_forgot_password()
    expect(login_page.page).to_have_url(re.compile(r"/forgot-password$"))


@pytest.mark.navigation
def test_create_account_link_opens_register_page(login_page):
    login_page.click_create_account()
    expect(login_page.page).to_have_url(re.compile(r"/register$"))


# ==================== Positive ====================

@pytest.mark.login
def test_login_with_second_user(login_page):
    login_page.login(EMAIL_NAAMA, PASSWORD_NAAMA)
    expect(login_page.page).to_have_url(URL_FINANCE_SITE)
    expect(login_page.dashboard_title).to_be_visible()


@pytest.mark.login
def test_logged_out_user_is_redirected_to_login(page: Page):
    page.goto("/wallets")
    expect(page).to_have_url(re.compile(r"/login$"))


# ==================== Negative ====================

@pytest.mark.login
def test_login_with_empty_fields_shows_both_errors(login_page):
    login_page.click_sign_in()
    expect(login_page.email_error).to_be_visible()
    expect(login_page.password_error).to_be_visible()
    expect(login_page.email_input).to_have_attribute("aria-invalid", "true")
    expect(login_page.password_input).to_have_attribute("aria-invalid", "true")
    expect(login_page.page).to_have_url(re.compile(r"/login$"))


@pytest.mark.login
def test_login_with_invalid_email_format(login_page):
    login_page.login("not-an-email", PASSWORD_YAEL)
    expect(login_page.email_error).to_be_visible()
    expect(login_page.password_error).to_be_hidden()
    expect(login_page.page).to_have_url(re.compile(r"/login$"))


@pytest.mark.login
def test_login_without_password(login_page):
    login_page.login(EMAIL_YAEL, "")
    expect(login_page.password_error).to_be_visible()
    expect(login_page.email_error).to_be_hidden()
    expect(login_page.page).to_have_url(re.compile(r"/login$"))


@pytest.mark.login
def test_login_with_wrong_password(login_page):
    login_page.login(EMAIL_YAEL, "WrongPassword123!")
    expect(login_page.login_error_alert).to_be_visible()
    expect(login_page.page).to_have_url(re.compile(r"/login$"))
    expect(login_page.dashboard_title).to_be_hidden()


@pytest.mark.login
def test_login_with_unregistered_email(login_page):
    login_page.login("not-registered-user@example.com", "SomePassword123!")
    expect(login_page.login_error_alert).to_be_visible()
    expect(login_page.page).to_have_url(re.compile(r"/login$"))
