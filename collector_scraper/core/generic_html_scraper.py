from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence
from urllib.parse import quote_plus, urljoin

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
    fallback_search_url_templates: Sequence[str] = ()
    max_items: int = 60
    _generic_stopwords = {
        "pokemon",
        "cards",
        "card",
        "booster",
        "set",
        "tcg",
        "the",
        "and",
    }

    def build_search_url(self, query: str) -> str:
        encoded_query = quote_plus(query.strip())
        return self.search_url_template.format(query=encoded_query)

    def search(self, query: str) -> List[Dict[str, Any]]:
        encoded_query = quote_plus(query.strip())
        candidate_urls = [self.build_search_url(query)]
        candidate_urls.extend(
            template.format(query=encoded_query) for template in self.fallback_search_url_templates
        )

        last_exception: Exception | None = None
        for url in candidate_urls:
            try:
                response = self._request(url)
            except Exception as exc:
                last_exception = exc
                continue

            parsed = self.parse_listing(response.text)
            if not parsed:
                parsed = self._parse_anchor_fallback(response.text)

            filtered = self._filter_by_query(parsed, query)
            if filtered:
                return filtered[: self.max_items]

        if last_exception is not None:
            raise last_exception
        return []

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

    def _parse_anchor_fallback(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        results: List[Dict[str, Any]] = []
        seen_keys = set()

        for anchor in soup.select("a[href]"):
            href = anchor.get("href")
            if not href:
                continue

            href_text = str(href).lower()
            if not any(
                marker in href_text
                for marker in ("/product/", "/products/", "/shop/product/", "/product-page/")
            ):
                continue

            title_text = anchor.get_text(" ", strip=True)
            parent_text = anchor.parent.get_text(" ", strip=True) if anchor.parent else ""
            grandparent_text = (
                anchor.parent.parent.get_text(" ", strip=True)
                if anchor.parent and anchor.parent.parent
                else ""
            )

            price = parse_price(f"{title_text} {parent_text} {grandparent_text}")
            if price is None:
                continue

            title = self._clean_title(title_text)
            if not title:
                title = self._clean_title(parent_text)
            if not title:
                continue

            item_url = urljoin(self.base_url, str(href))
            dedupe_key = (title.lower(), price, item_url)
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)

            results.append(
                self.normalize(
                    {
                        "title": title,
                        "price": price,
                        "source": self.source,
                        "url": item_url,
                    }
                )
            )

            if self.max_items and len(results) >= self.max_items:
                break

        return results

    def _filter_by_query(self, items: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        terms = self._query_terms(query)
        if not terms:
            return items

        filtered: List[Dict[str, Any]] = []
        for item in items:
            title = str(item.get("product_name") or item.get("title") or "").lower()
            if not title:
                continue
            if any(term in title for term in terms):
                filtered.append(item)
        return filtered

    def _query_terms(self, query: str) -> List[str]:
        tokens = [tok.lower() for tok in re.split(r"[^A-Za-z0-9]+", query) if tok]
        content_tokens = [tok for tok in tokens if len(tok) >= 3 and tok not in self._generic_stopwords]
        return content_tokens if content_tokens else [tok for tok in tokens if len(tok) >= 3]

    @staticmethod
    def _clean_title(text: str | None) -> str | None:
        if not text:
            return None

        title = re.sub(r"\bquick view\b", " ", text, flags=re.IGNORECASE)
        title = re.sub(r"\b(out of stock|sold out|add to cart|wishlist)\b", " ", title, flags=re.IGNORECASE)
        title = re.sub(r"\b(price|regular price|sale price)\b.*$", " ", title, flags=re.IGNORECASE)
        title = re.sub(r"\s+", " ", title).strip(" -|")
        return title if len(title) >= 4 else None

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
