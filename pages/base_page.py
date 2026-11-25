from urllib.parse import urljoin

from playwright.sync_api import Page
from utilities import config


class BasePage:
    PATH = "/"

    def __init__(self, page: Page) -> None:
        self.page = page


    def open(self) -> None:
        # Build the full address from the site URL + this page's path (no --base-url needed)
        self.page.goto(urljoin(config.URL_FINANCE_SITE, self.PATH), wait_until="domcontentloaded")