import re

from playwright.sync_api import Locator, Page

from pages.base_dummy_pay import BaseDummyPayPage


class ProfileSettingsPage(BaseDummyPayPage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def profile_settings_title(self) -> Locator:
        return self.page_heading("Profile & Settings")

    # ---------- Profile details (term -> value) ----------

    def _detail_value(self, term: str) -> Locator:
        """Returns the value shown next to a label like 'Email' in the profile details."""
        return self.main_area.locator(
            f"xpath=.//dt[normalize-space()='{term}']/following-sibling::dd[1]"
        )

    @property
    def user_id_value(self) -> Locator:
        return self._detail_value("User ID")

    @property
    def email_value(self) -> Locator:
        return self._detail_value("Email")

    @property
    def display_name_value(self) -> Locator:
        return self._detail_value("Display name")

    @property
    def preferred_currency_value(self) -> Locator:
        return self._detail_value("Preferred currency")

    # ---------- Edit forms ----------

    @property
    def display_name_input(self) -> Locator:
        return self.main_area.get_by_role("textbox", name="Display name")

    @property
    def save_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Save")

    @property
    def currency_select(self) -> Locator:
        return self.main_area.get_by_role("combobox", name="Currency")

    @property
    def change_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Change")

    @property
    def display_name_error(self) -> Locator:
        # הודעת שגיאה מתחת לשדה השם, למשל "Display name must be at least 2 characters."
        return self.main_area.get_by_role("alert").filter(has_text="Display name must be")

    @property
    def confirm_currency_change_btn(self) -> Locator:
        # כפתור האישור בחלון "Change preferred currency to GBP?"
        return self.page.get_by_role("alertdialog").get_by_role("button", name="Confirm change")

    # ---------- Toasts (הודעות זמניות שנעלמות אחרי כמה שניות) ----------

    @property
    def display_name_updated_toast(self) -> Locator:
        return self.page.get_by_role("region", name=re.compile("Notifications")).get_by_text("Display name updated.")

    def currency_changed_toast(self, currency: str) -> Locator:
        # "Preferred currency changed to GBP."
        return self.page.get_by_role("region", name=re.compile("Notifications")).get_by_text(
            f"Preferred currency changed to {currency}.")

    # ---------- Actions ----------

    def fill_display_name(self, name: str) -> None:
        self.display_name_input.fill(name)

    def click_save(self) -> None:
        self.save_btn.click()

    def select_currency(self, currency: str) -> None:
        self.select_option(self.currency_select, currency)

    def click_change(self) -> None:
        self.change_btn.click()

    # משנה את השם: ממלאת את השדה ולוחצת Save
    def change_display_name(self, name: str) -> None:
        self.fill_display_name(name)
        self.click_save()

    # משנה את המטבע המועדף: בחירה ברשימה, Change, ואישור בחלון ("Confirm change")
    def change_preferred_currency(self, currency: str) -> None:
        self.select_currency(currency)          # "GBP" בוחר את "GBP — British Pound"
        self.click_change()
        self.confirm_currency_change_btn.click()

    # ---------- Read data (return values, no checks) ----------

    # מחזירה את המטבע המועדף שמוגדר בהגדרות: "EUR — Euro" -> "EUR"
    def get_preferred_currency(self) -> str:
        """The preferred currency set in Settings: "EUR — Euro" -> "EUR" """
        text = self.preferred_currency_value.inner_text()   # "EUR — Euro"
        return text.split()[0]                              # "EUR"
