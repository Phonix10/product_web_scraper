from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseScraper(ABC):
    """Base contract every site adapter follows."""

    source: str = "unknown"
    timeout_seconds: int = 20
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def parse_listing(self, html: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def parse_sold(self, html: str) -> List[Dict[str, Any]]:
        return []

    def normalize(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "product_name": item.get("title"),
            "price": item.get("price"),
            "source": item.get("source", self.source),
            "price_type": item.get("price_type", "listing"),
            "url": item.get("url"),
            "currency": item.get("currency"),
        }

    def get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept-Language": "en-US,en;q=0.9",
        }
