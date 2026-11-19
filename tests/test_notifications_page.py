
from pages.notifications_page import NotificationsPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
import pytest


@pytest.mark.smoke
def test_notifications_page_is_displayed(notifications_page):
    expect(notifications_page.notifications_title).to_be_visible()
    expect(notifications_page.mark_all_read_btn).to_be_visible()
    expect(notifications_page.all_radio).to_be_visible()
    expect(notifications_page.unread_radio).to_be_visible()


@pytest.mark.navigation
def test_switch_between_all_and_unread(notifications_page):
    notifications_page.show_unread()
    expect(notifications_page.unread_radio).to_be_checked()

    notifications_page.show_all()
    expect(notifications_page.all_radio).to_be_checked()
