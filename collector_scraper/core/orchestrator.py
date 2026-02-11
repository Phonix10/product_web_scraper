from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Dict, List

from collector_scraper.core.base_scraper import BaseScraper
from collector_scraper.scrapers import build_tier1_scrapers


@dataclass
class OrchestrationResult:
    query: str
    items: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)


def run_all_scrapers(
    query: str,
    scrapers: Sequence[BaseScraper] | None = None,
    max_results_per_site: int = 40,
) -> OrchestrationResult:
    active_scrapers = list(scrapers) if scrapers else build_tier1_scrapers()
    result = OrchestrationResult(query=query)

    for scraper in active_scrapers:
        try:
            site_items = scraper.search(query)
            if max_results_per_site > 0:
                site_items = site_items[:max_results_per_site]
            result.items.extend(site_items)
        except Exception as exc:  # pragma: no cover
            result.errors.append({"source": scraper.source, "error": str(exc)})

    return result
