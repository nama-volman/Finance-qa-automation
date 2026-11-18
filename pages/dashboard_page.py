
from playwright.sync_api import Locator, Page ,expect
from pages.base_dummy_pay import BaseDummyPayPage

class DashboardPage(BaseDummyPayPage):
    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page) 






        