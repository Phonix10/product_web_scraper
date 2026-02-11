from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from collector_scraper.core.generic_html_scraper import GenericListScraper
from collector_scraper.utils.price_parser import parse_price


class TCGPlayerScraper(GenericListScraper):
    source = "tcgplayer"
    base_url = "https://www.tcgplayer.com"
    search_url_template = "https://www.tcgplayer.com/search/all/product?q={query}&view=grid"
    fallback_search_url_templates = (
        "https://www.tcgplayer.com/search/pokemon/product?q={query}&view=grid",
    )
    item_selector = ".search-result, .product-card, .search-layout__content .product"
    title_selectors = (
        ".search-result__title",
        ".product-card__title",
        ".product-card__product-name",
        "a[data-testid='productNameLink']",
        "a[href*='/product/']",
    )
    price_selectors = (
        ".inventory__price-with-shipping",
        ".search-result__market-price--value",
        ".product-card__market-price--value",
        ".product-card__price",
        "[data-testid='listingPrice']",
    )
    link_selectors = ("a[href*='/product/']",)

    def parse_listing(self, html: str) -> List[Dict[str, Any]]:
        parsed = super().parse_listing(html)
        if parsed:
            return parsed

        if self._page_requires_js(html):
            raise RuntimeError(
                "TCGPlayer returned a JavaScript-only page. "
                "Use browser automation for this source."
            )

        # Some variants expose JSON-LD product metadata.
        json_ld_results = self._parse_json_ld(html)
        if json_ld_results:
            return json_ld_results

        return self._parse_anchor_fallback(html)

    @staticmethod
    def _page_requires_js(html: str) -> bool:
        lowered = html.lower()
        return (
            "doesn't work properly without javascript" in lowered
            or "enable javascript to continue" in lowered
        )

    def _parse_json_ld(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        results: List[Dict[str, Any]] = []
        seen = set()

        for script in soup.select("script[type='application/ld+json']"):
            payload = script.get_text(strip=True)
            if not payload:
                continue
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                continue

            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue

                item_type = str(item.get("@type", "")).lower()
                if item_type not in {"product", "offer"}:
                    continue

                title = item.get("name") or item.get("title")
                offer = item.get("offers", item)
                if isinstance(offer, dict):
                    raw_price = offer.get("price")
                    url = offer.get("url") or item.get("url")
                else:
                    raw_price = None
                    url = item.get("url")

                price = parse_price(str(raw_price))
                if not title or price is None:
                    continue

                dedupe_key = (str(title).lower(), price, str(url or ""))
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)

                results.append(
                    self.normalize(
                        {
                            "title": re.sub(r"\s+", " ", str(title)).strip(),
                            "price": price,
                            "source": self.source,
                            "url": str(url) if url else None,
                        }
                    )
                )

        return results
