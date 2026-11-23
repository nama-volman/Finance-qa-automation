from pages.base_dummy_pay import BaseDummyPayPage
import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.forgot_password_page import ForgotPasswordPage
from pages.dashboard_page import DashboardPage
from pages.wallets_page import WalletsPage
from pages.send_money_page import SendMoneyPage
from pages.transaction_history_page import TransactionHistoryPage
from pages.payment_cards_page import PaymentCardsPage
from pages.bank_accounts_page import BankAccountsPage
from pages.notifications_page import NotificationsPage
from pages.profile_settings_page import ProfileSettingsPage
from utilities import config
from utilities import navbar_options as navbar


# גודל חלון הדפדפן בכל הטסטים: 1280x1080 במקום ברירת המחדל 1280x720.
# בחלון נמוך הדף מתארך כשהנתונים נטענים, ותפריט החשבון (בתחתית הסרגל) נדחף אל מחוץ למסך.
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 1080}}


@pytest.fixture(autouse=True)
def default_timeout(page: Page) -> None:
    page.set_default_timeout(config.DEFAULT_TIMEOUT_MS)

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    login = LoginPage(page)
    login.open()
    return login


@pytest.fixture
def forgot_password_page(page: Page) -> ForgotPasswordPage:
    forgot = ForgotPasswordPage(page)
    forgot.open()
    return forgot


@pytest.fixture
def logged_in(page):
    dummyPayPage = BaseDummyPayPage(page)
    dummyPayPage.open()
    dummyPayPage.login_with_valid_credentials()
    # Wait until the post-login redirect finishes, so the next click isn't lost
    expect(dummyPayPage.page_heading("Dashboard")).to_be_visible()
    yield dummyPayPage
    # dummyPayPage.logout()



@pytest.fixture
def dashboard_page(logged_in):
    return DashboardPage(logged_in.page)   # already here after login


@pytest.fixture
def wallets_page(logged_in):
    logged_in.navigate_to(navbar.WALLETS)  # click + verify URL
    return WalletsPage(logged_in.page)


@pytest.fixture
def send_money_page(logged_in):
    logged_in.navigate_to(navbar.SEND_MONEY)
    return SendMoneyPage(logged_in.page)




@pytest.fixture
def transaction_history_page(logged_in):
    logged_in.navigate_to(navbar.TRANSACTION_HISTORY)
    return TransactionHistoryPage(logged_in.page)


@pytest.fixture
def payment_cards_page(logged_in):
    logged_in.navigate_to(navbar.PAYMENT_CARDS)
    return PaymentCardsPage(logged_in.page)


@pytest.fixture
def bank_accounts_page(logged_in):
    logged_in.navigate_to(navbar.BANK_ACCOUNTS)
    return BankAccountsPage(logged_in.page)


@pytest.fixture
def notifications_page(logged_in):
    logged_in.navigate_to(navbar.NOTIFICATIONS)
    return NotificationsPage(logged_in.page)


@pytest.fixture
def profile_settings_page(logged_in):
    logged_in.navigate_to(navbar.PROFILE_SETTINGS)
    return ProfileSettingsPage(logged_in.page)



