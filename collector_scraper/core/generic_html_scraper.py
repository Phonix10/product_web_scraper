from __future__ import annotations

from typing import Any, Dict, List, Sequence
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

from collector_scraper.core.base_scraper import BaseScraper
from collector_scraper.utils.price_parser import parse_price


class GenericListScraper(BaseScraper):
    """Selector-driven HTML listing scraper."""

    base_url: str = ""
    search_url_template: str = ""
    item_selector: str = ""
    title_selectors: Sequence[str] = ()
    price_selectors: Sequence[str] = ()
    link_selectors: Sequence[str] = ()
    blocked_title_keywords: Sequence[str] = ()
    max_items: int = 60

    def build_search_url(self, query: str) -> str:
        encoded_query = quote_plus(query.strip())
        return self.search_url_template.format(query=encoded_query)

    def search(self, query: str) -> List[Dict[str, Any]]:
        url = self.build_search_url(query)
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return self.parse_listing(response.text)

    def parse_listing(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        containers = soup.select(self.item_selector)

        results: List[Dict[str, Any]] = []
        seen_keys = set()

        for container in containers:
            title = self._extract_text(container, self.title_selectors)
            if not title:
                continue

            title_lower = title.lower()
            if any(blocked.lower() in title_lower for blocked in self.blocked_title_keywords):
                continue

            price_text = self._extract_text(container, self.price_selectors)
            price = parse_price(price_text)
            if price is None:
                continue

            href = self._extract_href(container, self.link_selectors)
            item_url = urljoin(self.base_url, href) if href else None

            dedupe_key = (title.strip().lower(), price, item_url)
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)

            normalized = self.normalize(
                {
                    "title": title.strip(),
                    "price": price,
                    "source": self.source,
                    "url": item_url,
                }
            )
            results.append(normalized)

            if self.max_items and len(results) >= self.max_items:
                break

        return results

    @staticmethod
    def _extract_text(container: Any, selectors: Sequence[str]) -> str | None:
        for selector in selectors:
            node = container.select_one(selector)
            if node:
                text = node.get_text(" ", strip=True)
                if text:
                    return text
        return None

    @staticmethod
    def _extract_href(container: Any, selectors: Sequence[str]) -> str | None:
        for selector in selectors:
            node = container.select_one(selector)
            if node and node.has_attr("href"):
                href = node.get("href")
                if href:
                    return str(href)
        return None
