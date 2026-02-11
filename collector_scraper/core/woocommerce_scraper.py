from __future__ import annotations

from typing import Any, Dict, List
from urllib.parse import quote_plus

from collector_scraper.core.base_scraper import BaseScraper
from collector_scraper.utils.price_parser import parse_price


class WooCommerceStoreScraper(BaseScraper):
    """Scraper that uses WooCommerce Store API public product search."""

    base_url: str = ""
    per_page: int = 30

    def build_search_url(self, query: str) -> str:
        encoded_query = quote_plus(query.strip())
        return (
            f"{self.base_url.rstrip('/')}/wp-json/wc/store/v1/products"
            f"?search={encoded_query}&per_page={self.per_page}"
        )

    def search(self, query: str) -> List[Dict[str, Any]]:
        response = self._request(
            self.build_search_url(query),
            extra_headers={"Accept": "application/json"},
        )
        payload = response.json()
        return self.parse_listing(payload)

    def parse_listing(self, payload: Any) -> List[Dict[str, Any]]:
        if not isinstance(payload, list):
            return []

        results: List[Dict[str, Any]] = []
        for product in payload:
            if not isinstance(product, dict):
                continue

            title = product.get("name")
            if not title:
                continue

            price, currency = self._extract_price(product)
            if price is None:
                continue

            results.append(
                self.normalize(
                    {
                        "title": str(title).strip(),
                        "price": price,
                        "source": self.source,
                        "url": product.get("permalink"),
                        "currency": currency,
                    }
                )
            )
        return results

    @staticmethod
    def _extract_price(product: Dict[str, Any]) -> tuple[float | None, str | None]:
        prices = product.get("prices", {})
        if not isinstance(prices, dict):
            return None, None

        currency_code = prices.get("currency_code")
        minor_unit = prices.get("currency_minor_unit", 2)
        for key in ("price", "sale_price", "regular_price"):
            value = prices.get(key)
            numeric = WooCommerceStoreScraper._minor_unit_price(value, minor_unit)
            if numeric is not None:
                return numeric, currency_code

        # Some stores include user-facing text with currency symbol.
        for key in ("price_html",):
            value = prices.get(key)
            numeric = parse_price(str(value)) if value is not None else None
            if numeric is not None:
                return numeric, currency_code

        return None, currency_code

    @staticmethod
    def _minor_unit_price(raw: Any, minor_unit: Any) -> float | None:
        if raw is None:
            return None

        try:
            unit = int(minor_unit)
        except (TypeError, ValueError):
            unit = 2

        scale = 10 ** max(unit, 0)

        if isinstance(raw, (int, float)):
            return round(float(raw) / scale, 2)

        text = str(raw).strip()
        if not text:
            return None

        if text.isdigit():
            return round(float(int(text)) / scale, 2)

        return parse_price(text)
