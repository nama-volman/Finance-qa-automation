import re
from playwright.sync_api import Locator, Page

from pages.base_dummy_pay import BaseDummyPayPage


class NotificationsPage(BaseDummyPayPage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def notifications_title(self) -> Locator:
        return self.page_heading("Notifications")

    @property
    def mark_all_read_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Mark all as read")

    @property
    def all_radio(self) -> Locator:
        return self.main_area.get_by_role("radio", name="All")

    @property
    def unread_radio(self) -> Locator:
        return self.main_area.get_by_role("radio", name="Unread")

    @property
    def notifications(self) -> Locator:
        return self.main_area.get_by_role("listitem")

    @property
    def all_caught_up_text(self) -> Locator:
        return self.main_area.get_by_text("You're all caught up")

    @property
    def mark_read_btns(self) -> Locator:
        # the "Mark read" button inside each unread notification (not "Mark all as read")
        return self.notifications.get_by_role("button", name=re.compile(r"^Mark( as)? read$"))


    # ---------- Actions ----------

    def show_all(self) -> None:
        self.all_radio.click()

    def show_unread(self) -> None:
        self.unread_radio.click()

    def click_mark_all_read(self) -> None:
        self.mark_all_read_btn.click()
    
    def mark_first_as_read(self) -> None:
        self.mark_read_btns.first.click()
