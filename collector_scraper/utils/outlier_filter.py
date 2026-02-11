from __future__ import annotations

from statistics import median
from typing import Dict, Iterable, List


def _clean_prices(prices: Iterable[float | int | None]) -> List[float]:
    cleaned: List[float] = []
    for raw in prices:
        if raw is None:
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        if value > 0:
            cleaned.append(value)
    cleaned.sort()
    return cleaned


def _trim_prices(prices: List[float], trim_ratio: float) -> List[float]:
    if not prices:
        return []

    if trim_ratio <= 0 or len(prices) < 5:
        return prices

    trim_count = int(len(prices) * trim_ratio)
    if trim_count == 0:
        return prices

    start = trim_count
    end = len(prices) - trim_count
    if start >= end:
        return prices

    return prices[start:end]


def _iqr_filter(prices: List[float], multiplier: float = 1.5) -> List[float]:
    if len(prices) < 4:
        return prices

    midpoint = len(prices) // 2
    lower = prices[:midpoint]
    upper = prices[midpoint:] if len(prices) % 2 == 0 else prices[midpoint + 1 :]

    if not lower or not upper:
        return prices

    q1 = median(lower)
    q3 = median(upper)
    iqr = q3 - q1

    if iqr == 0:
        return prices

    low_bound = q1 - (multiplier * iqr)
    high_bound = q3 + (multiplier * iqr)

    filtered = [price for price in prices if low_bound <= price <= high_bound]
    return filtered or prices


def calculate_market_stats(
    prices: Iterable[float | int | None],
    trim_ratio: float = 0.1,
    iqr_multiplier: float = 1.5,
) -> Dict[str, float | int | None]:
    cleaned = _clean_prices(prices)
    if not cleaned:
        return {
            "raw_count": 0,
            "count": 0,
            "high": None,
            "low": None,
            "average": None,
            "median": None,
        }

    trimmed = _trim_prices(cleaned, trim_ratio)
    filtered = _iqr_filter(trimmed, iqr_multiplier)

    return {
        "raw_count": len(cleaned),
        "count": len(filtered),
        "high": round(max(filtered), 2),
        "low": round(min(filtered), 2),
        "average": round(sum(filtered) / len(filtered), 2),
        "median": round(float(median(filtered)), 2),
    }
