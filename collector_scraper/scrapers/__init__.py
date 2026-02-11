"""Scraper adapters for Tier-1 sites."""

from collector_scraper.scrapers.beyondgaming import BeyondGamingScraper
from collector_scraper.scrapers.cardmarket import CardmarketScraper
from collector_scraper.scrapers.coolstuffinc import CoolStuffIncScraper
from collector_scraper.scrapers.ebay import EbayScraper
from collector_scraper.scrapers.pokedex import PokedexScraper
from collector_scraper.scrapers.pokevolt import PokevoltScraper
from collector_scraper.scrapers.tcgplayer import TCGPlayerScraper
from collector_scraper.scrapers.toysonfire import ToysOnFireScraper
from collector_scraper.scrapers.trollandtoad import TrollAndToadScraper


def build_tier1_scrapers():
    return [
        EbayScraper(),
        TCGPlayerScraper(),
        CardmarketScraper(),
        TrollAndToadScraper(),
        CoolStuffIncScraper(),
        PokevoltScraper(),
        PokedexScraper(),
        BeyondGamingScraper(),
        ToysOnFireScraper(),
    ]


__all__ = [
    "build_tier1_scrapers",
    "EbayScraper",
    "TCGPlayerScraper",
    "CardmarketScraper",
    "TrollAndToadScraper",
    "CoolStuffIncScraper",
    "PokevoltScraper",
    "PokedexScraper",
    "BeyondGamingScraper",
    "ToysOnFireScraper",
]
