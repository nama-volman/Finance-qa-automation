
from playwright.sync_api import Locator, Page ,expect
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

    # ---------- Actions ----------

    def show_all(self) -> None:
        self.all_radio.click()

    def show_unread(self) -> None:
        self.unread_radio.click()

    def click_mark_all_read(self) -> None:
        self.mark_all_read_btn.click()
