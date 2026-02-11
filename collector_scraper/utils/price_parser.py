from __future__ import annotations
import re


_NUMBER_TOKEN = re.compile(r"\d[\d,\.]*")
_DECIMAL_SUFFIX_DOT = re.compile(r"\.\d{1,2}$")
_DECIMAL_SUFFIX_COMMA = re.compile(r",\d{1,2}$")


def detect_currency(text: str) -> str:
    if "₹" in text:
        return "INR"
    if "$" in text:
        return "USD"
    if "€" in text:
        return "EUR"
    if "C$" in text or "CAD" in text:
        return "CAD"
    return "UNKNOWN"


def parse_price(text: str | None) -> tuple[float | None, str]:
    if not text:
        return None, "UNKNOWN"

    currency = detect_currency(text)

    match = _NUMBER_TOKEN.search(text)
    if not match:
        return None, currency

    cleaned = match.group(0)

    if "," in cleaned and "." in cleaned:
        if _DECIMAL_SUFFIX_DOT.search(cleaned):
            normalized = cleaned.replace(",", "")
        elif _DECIMAL_SUFFIX_COMMA.search(cleaned):
            normalized = cleaned.replace(".", "").replace(",", ".")
        else:
            normalized = cleaned.replace(",", "")
    elif "," in cleaned:
        if _DECIMAL_SUFFIX_COMMA.search(cleaned):
            normalized = cleaned.replace(",", ".")
        else:
            normalized = cleaned.replace(",", "")
    else:
        normalized = cleaned

    try:
        value = float(normalized)
    except ValueError:
        return None, currency

    if value <= 0:
        return None, currency

    return value, currency
