import os

from dotenv import load_dotenv

load_dotenv(override=True)

DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "20000"))
URL_FINANCE_SITE="https://dummypay.vercel.app/"


SUPABASE_URL= os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY=os.getenv("SUPABASE_ANON_KEY")

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


#profile-settings
# שם תצוגה תקין: 2 עד 50 תווים
PROFILE_DETAILS = {
    "valid_display_name": "QA Tester",
    "too_short_display_name": "A",           # תו אחד - קצר מדי
    "too_long_display_name": "A" * 51,       # 51 תווים - ארוך מדי
}


#bank-account
# מספר חשבון תקין: 4 עד 20 ספרות
BANK_ACCOUNT_DETAILS = {
    "holder_name": "Israel Israeli",
    "bank_name": "Test Bank",
    "country": "Israel",
    "currency": "ILS",
    "valid_account_number": "12345678",                    # 8 ספרות - תקין
    "too_short_account_number": "123",                     # 3 ספרות - קצר מדי
    "too_long_account_number": "123456789012345678901",    # 21 ספרות - ארוך מדי
}

AMOUNT_TO_SEND=100
NOT_REGISTERED_EMAIL = "noexists@example.com"



#transaction-history-filters
HISTORY_FILTERS = {
    "future_date": "2027-01-01",
    "later_date": "2026-11-25",
    "day_with_two_transactions": "2026-11-19",
    "day_text": "Nov 19, 2026",
    "currency": "EUR",
    "currency_symbol": "€",
    "type": "Received",
}
