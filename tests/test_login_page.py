
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest
from utilities.config import URL_FINANCE_SITE, EMAIL_YAEL, PASSWORD_YAEL, EMAIL_NAAMA, PASSWORD_NAAMA


@pytest.mark.smoke
def test_login_to_finance_site(page: Page):
    loginPage = LoginPage(page)
    loginPage.open()
    
    loginPage.page.pause()
    loginPage.verify_login_page_title()  # בדיקה שהכותרת של הדף היא DummyPay
    expect(loginPage.login_page_title).to_be_visible() 
    
    loginPage.login_with_valid_credentials()
    expect(loginPage.page).to_have_url(URL_FINANCE_SITE)
    expect(loginPage.dashboard_title).to_be_visible()




   