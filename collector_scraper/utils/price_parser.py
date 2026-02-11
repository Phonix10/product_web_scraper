from __future__ import annotations

import re


_NUMBER_TOKEN = re.compile(r"\d[\d,\.]*")
_DECIMAL_SUFFIX_DOT = re.compile(r"\.\d{1,2}$")
_DECIMAL_SUFFIX_COMMA = re.compile(r",\d{1,2}$")


def parse_price(text: str | None) -> float | None:
    if not text:
        return None

    match = _NUMBER_TOKEN.search(text)
    if not match:
        return None
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
        return None

    if value <= 0:
        return None

    return value
