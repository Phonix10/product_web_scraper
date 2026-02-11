from __future__ import annotations

import re
from typing import Any, Dict, List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from collector_scraper.core.base_scraper import BaseScraper
from collector_scraper.utils.price_parser import parse_price


class PokevoltScraper(BaseScraper):
    source = "pokevolt"
    base_url = "https://www.pokevolt.shop"
    max_items = 60

    def search(self, query: str) -> List[Dict[str, Any]]:
        encoded_query = quote_plus(query.strip())
        # Wix storefront currently exposes products under /shop and query-filtered views.
        candidate_urls = (
            f"{self.base_url}/shop?page=1&search={encoded_query}",
            f"{self.base_url}/shop?query={encoded_query}",
            f"{self.base_url}/shop",
        )

        for url in candidate_urls:
            try:
                response = self._request(url)
            except Exception:
                continue
            parsed = self.parse_listing(response.text)
            filtered = self._filter_by_query(parsed, query)
            if filtered:
                return filtered[: self.max_items]

        return []

    def parse_listing(self, html: Any) -> List[Dict[str, Any]]:
        if not isinstance(html, str):
            return []

        soup = BeautifulSoup(html, "html.parser")
        results: List[Dict[str, Any]] = []
        seen = set()

        for anchor in soup.select("a[href*='/shop/product/'], a[href*='/product-page/']"):
            href = str(anchor.get("href") or "").strip()
            if not href:
                continue

            title = self._clean_title(anchor.get_text(" ", strip=True))
            parent_text = anchor.parent.get_text(" ", strip=True) if anchor.parent else ""
            price = parse_price(f"{anchor.get_text(' ', strip=True)} {parent_text}")
            if not title or price is None:
                continue

            normalized = self.normalize(
                {
                    "title": title,
                    "price": price,
                    "source": self.source,
                    "url": href if href.startswith("http") else f"{self.base_url}{href}",
                }
            )
            dedupe_key = (
                str(normalized.get("product_name", "")).lower(),
                normalized.get("price"),
                normalized.get("url"),
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            results.append(normalized)
            if len(results) >= self.max_items:
                break

        return results

    @staticmethod
    def _filter_by_query(items: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        terms = [token.lower() for token in re.split(r"[^A-Za-z0-9]+", query) if len(token) >= 3]
        if not terms:
            return items
        return [
            item
            for item in items
            if any(term in str(item.get("product_name") or "").lower() for term in terms)
        ]

    @staticmethod
    def _clean_title(text: str | None) -> str | None:
        if not text:
            return None
        title = re.sub(r"\bquick view\b", " ", text, flags=re.IGNORECASE)
        title = re.sub(r"\b(price|regular price|sale price)\b.*$", " ", title, flags=re.IGNORECASE)
        title = re.sub(r"\b(out of stock|sold out)\b", " ", title, flags=re.IGNORECASE)
        title = re.sub(r"\s+", " ", title).strip(" -|")
        return title if len(title) >= 4 else None
