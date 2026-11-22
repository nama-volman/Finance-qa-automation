import re

# All currencies supported by the site
CURRENCIES = ["ILS", "USD", "EUR", "GBP"]


def parse_amount_to_number(text: str) -> float:
    """
    Turns a money text from the site into a number.
        '≈ €3,635.99'  -> 3635.99
        '₪13,000.00'   -> 13000.0
        '−₪100.00'     -> -100.0   (the site uses the unicode minus sign '−')
    """
    cleaned = text.replace("−", "-").replace(",", "")
    match = re.search(r"-?\d+(\.\d+)?", cleaned)
    if not match:
        raise ValueError(f"No amount found in text: {text!r}")
    # keep the minus sign even when a currency symbol sits between it and the digits
    sign = -1 if "-" in cleaned[: match.start() + 1] else 1
    return sign * abs(float(match.group()))


# ממירה סכום בין המטבע המועדף למטבע אחר, לפי השערים מהמטבע המועדף.
# מהמועדף - כופלים בשער. אל המועדף - מחלקים בשער.
def convert_with_preferred(amount: float, from_currency: str, to_currency: str,
                           preferred: str, rates: dict[str, float]) -> float:
    """
    Converts between the preferred currency and another currency.

    `rates` = the Exchange rates card: how much of each currency equals
    1 unit of the preferred currency. For preferred EUR:
        {"ILS": 3.672007, "USD": 1.097333, "GBP": 0.837924}

    From the preferred currency -> multiply:  100 EUR -> ILS = 100 * 3.672007 = 367.20
    To the preferred currency   -> divide:    100 ILS -> EUR = 100 / 3.672007 = 27.23
    """
    if from_currency == preferred:
        return amount * rates[to_currency]
    return amount / rates[from_currency]
