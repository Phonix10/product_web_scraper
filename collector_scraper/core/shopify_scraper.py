from __future__ import annotations

from typing import Any, Dict, List, Sequence
from urllib.parse import quote_plus, urljoin

from collector_scraper.core.base_scraper import BaseScraper
from collector_scraper.utils.price_parser import parse_price


class ShopifyPredictiveScraper(BaseScraper):
    """Scraper for Shopify stores using predictive search JSON."""

    base_url: str = ""
    max_items: int = 60
    fallback_html_templates: Sequence[str] = ()

    def build_predictive_url(self, query: str) -> str:
        encoded_query = quote_plus(query.strip())
        return (
            f"{self.base_url.rstrip('/')}/search/suggest.json?"
            f"q={encoded_query}&resources[type]=product&resources[limit]={self.max_items}"
        )

    def search(self, query: str) -> List[Dict[str, Any]]:
        # First try the Shopify predictive endpoint.
        try:
            response = self._request(
                self.build_predictive_url(query),
                extra_headers={"Accept": "application/json"},
            )
            payload = response.json()
            parsed = self.parse_listing(payload)
            if parsed:
                return parsed[: self.max_items]
        except Exception:
            pass

        # Fall back to HTML search pages for themes that disable suggest.json.
        encoded_query = quote_plus(query.strip())
        templates = self.fallback_html_templates or (
            f"{self.base_url.rstrip('/')}/search?q={{query}}&type=product",
            f"{self.base_url.rstrip('/')}/search?q={{query}}",
        )
        for template in templates:
            try:
                response = self._request(template.format(query=encoded_query))
            except Exception:
                continue
            html_results = self._parse_html_listing(response.text)
            if html_results:
                return html_results[: self.max_items]

        return []

    def parse_listing(self, payload: Any) -> List[Dict[str, Any]]:
        if not isinstance(payload, dict):
            return []

        products = (
            payload.get("resources", {})
            .get("results", {})
            .get("products", [])
        )
        if not isinstance(products, list):
            return []

        results: List[Dict[str, Any]] = []
        for product in products:
            if not isinstance(product, dict):
                continue

            title = product.get("title")
            if not title:
                continue

            price = self._extract_price_from_product(product)
            if price is None:
                continue

            raw_url = str(product.get("url") or product.get("path") or "")
            if not raw_url:
                continue

            results.append(
                self.normalize(
                    {
                        "title": str(title).strip(),
                        "price": price,
                        "source": self.source,
                        "url": urljoin(self.base_url, raw_url),
                    }
                )
            )
        return results

    def _parse_html_listing(self, html: str) -> List[Dict[str, Any]]:
        from collector_scraper.core.generic_html_scraper import GenericListScraper

        class _Fallback(GenericListScraper):
            pass

        fallback = _Fallback()
        fallback.source = self.source
        fallback.base_url = self.base_url
        fallback.item_selector = ".card-wrapper, .grid__item, .product-item, .product-card"
        fallback.title_selectors = (
            "a.full-unstyled-link",
            ".card__heading a",
            ".product-item__title",
            "a[href*='/products/']",
        )
        fallback.price_selectors = (
            ".price-item--last",
            ".price-item--regular",
            ".price",
            ".money",
        )
        fallback.link_selectors = (
            "a.full-unstyled-link",
            ".card__heading a",
            "a[href*='/products/']",
        )
        fallback.max_items = self.max_items
        return fallback.parse_listing(html) or fallback._parse_anchor_fallback(html)

    @staticmethod
    def _extract_price_from_product(product: Dict[str, Any]) -> float | None:
        direct_candidates = (
            product.get("price"),
            product.get("price_min"),
            product.get("price_max"),
            product.get("compare_at_price"),
        )
        for candidate in direct_candidates:
            price = ShopifyPredictiveScraper._normalize_shopify_price(candidate)
            if price is not None:
                return price

        text_candidates = (
            product.get("price_varies"),
            product.get("price_range"),
            product.get("formatted_price"),
        )
        for candidate in text_candidates:
            price = parse_price(str(candidate))
            if price is not None:
                return price
        return None

    @staticmethod
    def _normalize_shopify_price(raw: Any) -> float | None:
        if raw is None:
            return None

        if isinstance(raw, (int, float)):
            value = float(raw)
            # Predictive API often returns cents.
            if value > 10000:
                return round(value / 100.0, 2)
            return round(value, 2)

        text = str(raw).strip()
        if not text:
            return None

        if text.isdigit():
            value = float(int(text))
            if value > 10000:
                return round(value / 100.0, 2)
            return round(value, 2)

        return parse_price(text)
