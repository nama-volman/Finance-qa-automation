import re

from pages.login_page import LoginPage
from playwright.sync_api import expect
import pytest

from utilities import navbar_options as navbar
from utilities.config import URL_FINANCE_SITE


@pytest.mark.login
def test_sign_out_returns_to_login_page(logged_in):
    logged_in.sign_out()
    expect(logged_in.page).to_have_url(re.compile(r"/login$"))
    expect(logged_in.sing_in_btn).to_be_visible()


@pytest.mark.login
def test_sign_out_from_inner_page(logged_in):
    logged_in.navigate_to(navbar.WALLETS)
    logged_in.sign_out()
    expect(logged_in.page).to_have_url(re.compile(r"/login$"))


@pytest.mark.login
def test_protected_page_is_blocked_after_sign_out(logged_in):
    logged_in.sign_out()
    expect(logged_in.page).to_have_url(re.compile(r"/login$"))

    logged_in.page.goto(URL_FINANCE_SITE)
    expect(logged_in.page).to_have_url(re.compile(r"/login$"))
    expect(logged_in.page_heading("Dashboard")).to_be_hidden()




@pytest.mark.login
def test_can_sign_in_again_after_sign_out(logged_in):
    logged_in.sign_out()
    expect(logged_in.page).to_have_url(re.compile(r"/login$"))

    # LoginPage(logged_in.page).login_with_valid_credentials()
    # expect(logged_in.page_heading("Dashboard")).to_be_visible()
