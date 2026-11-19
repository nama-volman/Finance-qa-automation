import re


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
