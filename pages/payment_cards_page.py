
import re

from playwright.sync_api import Locator, Page, expect

from pages.base_dummy_pay import BaseDummyPayPage


class PaymentCardsPage(BaseDummyPayPage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def cards_title(self) -> Locator:
        return self.page_heading("Payment Cards")

    @property
    def add_card_btn(self) -> Locator:
        return self.main_area.get_by_role("button", name="Add card")

    @property
    def simulated_alert(self) -> Locator:
        return self.main_area.get_by_role("alert")

    @property
    def empty_state_text(self) -> Locator:
        return self.main_area.get_by_text("No cards yet")

    @property  # כל הכרטיסים ברשימה
    def card_items(self) -> Locator:
        return self.page.get_by_test_id("card-item")

    # מוצאת כרטיס לפי 3 הפרטים שמוצגים עליו: 4 ספרות אחרונות, שם בעל הכרטיס ותוקף
    def find_card(self, last4: str, holder: str, expiry: str) -> Locator:
        return (self.card_items
                .filter(has_text=last4)
                .filter(has_text=holder)
                .filter(has_text=f"Exp {expiry}"))

    # ---------- "Add a simulated card" dialog ----------

    @property
    def add_card_dialog(self) -> Locator:
        return self.page.get_by_role("dialog", name="Add a simulated card")

    @property
    def cardholder_name_input(self) -> Locator:
        return self.add_card_dialog.get_by_role("textbox", name="Cardholder name")

    @property
    def card_number_input(self) -> Locator:
        return self.add_card_dialog.get_by_role("textbox", name="Card number")

    @property
    def expiry_input(self) -> Locator:
        return self.add_card_dialog.get_by_role("textbox", name="Expiry (MM/YY)")

    @property
    def cvv_input(self) -> Locator:
        return self.add_card_dialog.get_by_role("textbox", name="CVV")

    @property
    def dialog_add_btn(self) -> Locator:
        return self.add_card_dialog.get_by_role("button", name="Add card")

    @property
    def dialog_cancel_btn(self) -> Locator:
        return self.add_card_dialog.get_by_role("button", name="Cancel")

    @property
    def dialog_close_btn(self) -> Locator:
        return self.add_card_dialog.get_by_role("button", name="Close")
    @property
    def card_added_toast(self)-> Locator:
         return self.page.get_by_role("region", name=re.compile("Notifications")).get_by_text("Simulated card added")

    @property
    def card_removed_toast(self) -> Locator:
        # הודעה זמנית (toast) שמופיעה אחרי מחיקת כרטיס ונעלמת אחרי כמה שניות
        return self.page.get_by_role("region", name=re.compile("Notifications")).get_by_text("Card removed.")

    @property
    def invalid_card_number_message(self)-> Locator:
        return self.add_card_dialog.get_by_text("Card number is not valid (checksum failed).")

    @property
    def  invalid_expiry_date_message(self)-> Locator:
        return self.add_card_dialog.get_by_text("This card has expired.")



    # ---------- Actions ----------

    def click_add_card(self) -> None:
        self.add_card_btn.click()

    def cancel_dialog(self) -> None:
        self.dialog_cancel_btn.click()

    def fill_card_form(self, name: str, number: str, expiry: str, cvv: str) -> None:
        """Fills the form only - does not submit."""
        self.cardholder_name_input.fill(name)
        self.card_number_input.fill(number)
        self.expiry_input.fill(expiry)
        self.cvv_input.fill(cvv)

    def click_dialog_add(self) -> None:
        self.dialog_add_btn.click()

    # מוחקת כרטיס לפי 3 הפרטים: לחיצה על Remove בכרטיס ואז אישור בחלון
    def delete_card(self, last4: str, holder: str, expiry: str) -> None:
        self.find_card(last4, holder, expiry).first.get_by_role("button", name="Remove").click()
        self.page.get_by_role("alertdialog").get_by_role("button", name="Remove").click()


    def add_card(self, name: str, number: str, expiry: str, cvv: str)-> None:
        self.click_add_card()
        expect(self.add_card_dialog).to_be_visible()
        self.fill_card_form(name,number,expiry,cvv)
        self.click_dialog_add()
