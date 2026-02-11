from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BaseScraper(ABC):
    """Base contract every site adapter follows."""

    source: str = "unknown"
    connect_timeout_seconds: int = 10
    read_timeout_seconds: int = 20
    max_retries: int = 2
    backoff_factor: float = 0.7
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    _session: requests.Session | None = None

    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def parse_listing(self, payload: Any) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def parse_sold(self, payload: Any) -> List[Dict[str, Any]]:
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
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }

    def _build_session(self) -> requests.Session:
        retry_strategy = Retry(
            total=self.max_retries,
            connect=self.max_retries,
            read=self.max_retries,
            status=max(1, self.max_retries - 1),
            allowed_methods={"GET"},
            status_forcelist=(429, 500, 502, 503, 504),
            backoff_factor=self.backoff_factor,
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _get_session(self) -> requests.Session:
        if self._session is None:
            self._session = self._build_session()
        return self._session

    def _request(
        self,
        url: str,
        extra_headers: Mapping[str, str] | None = None,
        allowed_statuses: tuple[int, ...] = (),
    ) -> requests.Response:
        headers = self.get_headers().copy()
        if extra_headers:
            headers.update(extra_headers)

        response = self._get_session().get(
            url,
            headers=headers,
            timeout=(self.connect_timeout_seconds, self.read_timeout_seconds),
        )

        if response.status_code not in allowed_statuses:
            response.raise_for_status()

        return response
