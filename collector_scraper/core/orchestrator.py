from __future__ import annotations

import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Dict, List

from collector_scraper.core.base_scraper import BaseScraper
from collector_scraper.scrapers import build_tier1_scrapers


@dataclass
class OrchestrationResult:
    query: str
    items: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    durations_ms: Dict[str, int] = field(default_factory=dict)


def _run_single_scraper(scraper: BaseScraper, query: str) -> tuple[str, List[Dict[str, Any]], str | None, int]:
    started = time.perf_counter()
    try:
        items = scraper.search(query)
        elapsed = int((time.perf_counter() - started) * 1000)
        return scraper.source, items, None, elapsed
    except Exception as exc:  # pragma: no cover
        elapsed = int((time.perf_counter() - started) * 1000)
        return scraper.source, [], str(exc), elapsed


def run_all_scrapers(
    query: str,
    scrapers: Sequence[BaseScraper] | None = None,
    max_results_per_site: int = 40,
    max_workers: int = 5,
) -> OrchestrationResult:
    active_scrapers = list(scrapers) if scrapers else build_tier1_scrapers()
    result = OrchestrationResult(query=query)

    workers = max(1, min(max_workers, len(active_scrapers)))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_single_scraper, scraper, query) for scraper in active_scrapers]
        for future in as_completed(futures):
            source, site_items, error, elapsed = future.result()
            result.durations_ms[source] = elapsed
            if error:
                result.errors.append({"source": source, "error": error})
                continue
            if max_results_per_site > 0:
                site_items = site_items[:max_results_per_site]
            result.items.extend(site_items)

    return result
