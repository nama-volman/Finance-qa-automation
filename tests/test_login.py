import re

import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from utilities.config import URL_FINANCE_SITE


@pytest.mark.smoke
def test_login_to_finance_site(page: Page):
    loginPage = LoginPage(page)
    loginPage.open()
    loginPage.page.pause()
    #loginPage.clickLogIn()