from __future__ import annotations

import re
import time
import requests
from typing import Tuple, Optional




_NUMBER_TOKEN = re.compile(r"\d[\d,\.]*")
_DECIMAL_SUFFIX_DOT = re.compile(r"\.\d{1,2}$")
_DECIMAL_SUFFIX_COMMA = re.compile(r",\d{1,2}$")


def detect_currency(text: str) -> str:
    text = text.upper()

    if "₹" in text:
        return "INR"
    if "$" in text:
        return "USD"
    if "€" in text:
        return "EUR"
    if "C$" in text or "CAD" in text:
        return "CAD"
    if "£" in text:
        return "GBP"

    return "UNKNOWN"


def parse_price(text: str | None) -> Tuple[Optional[float], str]:
    """
    Extract numeric price and detect currency.
    Returns: (value, currency)
    """
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


# -------------------------------
# LIVE EXCHANGE RATE SECTION
# -------------------------------

BASE_CURRENCY = "INR"
EXCHANGE_API = "https://api.exchangerate.host/latest"

_cached_rates = None
_last_fetch_time = 0
CACHE_DURATION_SECONDS = 3600  # 1 hour


def fetch_exchange_rates(base: str = BASE_CURRENCY) -> dict:
    """
    Fetch live exchange rates from API.
    """
    response = requests.get(
        EXCHANGE_API,
        params={"base": base},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    return data["rates"]


def get_cached_rates() -> dict:
    """
    Cache exchange rates for 1 hour.
    """
    global _cached_rates, _last_fetch_time

    if (
        _cached_rates is None
        or time.time() - _last_fetch_time > CACHE_DURATION_SECONDS
    ):
        _cached_rates = fetch_exchange_rates()
        _last_fetch_time = time.time()

    return _cached_rates


def convert_to_inr(price: float, currency: str) -> Optional[float]:
    """
    Convert any currency to INR using live rates.
    """

    if currency == "INR":
        return price

    rates = get_cached_rates()

    if currency not in rates:
        return None

    # Since base is INR:
    # rates["USD"] means 1 INR = X USD
    # So USD to INR = price / rate
    rate = rates[currency]

    if rate == 0:
        return None

    return price / rate


# -------------------------------
# MAIN UTILITY FUNCTION
# -------------------------------

def parse_and_convert_to_inr(text: str | None) -> Optional[float]:
    """
    Full pipeline:
    - Parse price
    - Detect currency
    - Convert to INR
    """

    price, currency = parse_price(text)

    if not price:
        return None

    converted = convert_to_inr(price, currency)

    if not converted:
        return None

    return round(converted, 2)
