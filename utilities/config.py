import os
from dotenv import load_dotenv

load_dotenv(override=True)

DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "20000"))
URL_FINANCE_SITE="https://dummypay.vercel.app/"

# sign-in
EMAIL_YAEL = os.getenv("EMAIL_YAEL")
PASSWORD_YAEL = os.getenv("PASSWORD_YAEL")
EMAIL_NAAMA = os.getenv("EMAIL_NAAMA")
PASSWORD_NAAMA = os.getenv("PASSWORD_NAAMA")


# wallets
# ערכים לא תקינים לבדיקות השליליות של מחשבון ההמרה (Wallets).
# אפשר לשנות אותם מבחוץ דרך קובץ .env או משתנה סביבה באותו שם.
INVALID_AMOUNT_NOT_A_NUMBER = os.getenv("INVALID_AMOUNT_NOT_A_NUMBER", "STRING")
INVALID_AMOUNT_TOO_MANY_DECIMALS = os.getenv("INVALID_AMOUNT_TOO_MANY_DECIMALS", "12.3455476")


#payment-card
CARD_DETAILS = {
    "cardholder_name": "Israel Israeli",
    "valid_card_number": "4111111111111111",
    "invalid_card_number": "3111111111111111",
    "valid_expiry": "12/30",
    "invalid_expiry": "12/24",
    "cvv": "123",
}
