import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "15000"))
URL_FINANCE_SITE="https://dummypay.vercel.app/"

EMAIL_YAEL = os.getenv("EMAIL_YAEL")
PASSWORD_YAEL = os.getenv("PASSWORD_YAEL")
EMAIL_NAAMA = os.getenv("EMAIL_NAAMA")
PASSWORD_NAAMA = os.getenv("PASSWORD_NAAMA")    