from __future__ import annotations

import argparse
from collections import Counter

from collector_scraper.core.orchestrator import run_all_scrapers
from collector_scraper.utils.outlier_filter import calculate_market_stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Tier-1 product scrapers")
    parser.add_argument("query", help="Product search query")
    parser.add_argument(
        "--max-results-per-site",
        type=int,
        default=30,
        help="Cap listings retained per site (default: 30)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Number of site scrapers to run in parallel (default: 5)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    orchestration = run_all_scrapers(
        query=args.query,
        max_results_per_site=args.max_results_per_site,
        max_workers=args.max_workers,
    )

    items = orchestration.items
    prices = [item.get("price") for item in items]
    stats = calculate_market_stats(prices)

    print(f"Query: {args.query}")
    print(f"Listings collected: {len(items)}")

    source_counts = Counter(item.get("source") for item in items)
    if source_counts:
        print("Source breakdown:")
        for source, count in sorted(source_counts.items()):
            print(f"  - {source}: {count}")

    if orchestration.durations_ms:
        print("Site timings (ms):")
        for source, elapsed in sorted(orchestration.durations_ms.items()):
            print(f"  - {source}: {elapsed}")

    print("Market stats:")
    print(f"  - raw_count: {stats['raw_count']}")
    print(f"  - count: {stats['count']}")
    print(f"  - high: {stats['high']}")
    print(f"  - low: {stats['low']}")
    print(f"  - average: {stats['average']}")
    print(f"  - median: {stats['median']}")

    if orchestration.errors:
        print("Errors:")
        for error in orchestration.errors:
            print(f"  - {error['source']}: {error['error']}")


if __name__ == "__main__":
    main()
