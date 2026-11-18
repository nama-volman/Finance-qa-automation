from pages.base_page import NavBar
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest



#  loginPage.loginAndNavigate(NavBar.dashboard)