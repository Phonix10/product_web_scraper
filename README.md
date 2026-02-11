# product_web_scraper

Tier-1 multi-site card/product scraper foundation with a unified adapter pattern.

## Targets (Tier-1)

- eBay
- TCGPlayer
- Cardmarket
- Troll and Toad
- CoolStuffInc
- Pokevolt
- Pokedex.in
- Beyond Gaming
- ToysOnFire

## Project Layout

```text
collector_scraper/
  core/
    base_scraper.py
    generic_html_scraper.py
    orchestrator.py
  scrapers/
    ebay.py
    tcgplayer.py
    cardmarket.py
    trollandtoad.py
    coolstuffinc.py
    pokevolt.py
    pokedex.py
    beyondgaming.py
    toysonfire.py
  utils/
    price_parser.py
    outlier_filter.py
run.py
requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python run.py "pokemon charizard base set 1999"
```

Optional arguments:

```bash
python run.py "pokemon charizard base set 1999" --max-results-per-site 20
python run.py "pokemon charizard base set 1999" --max-workers 6
```

## Notes

- Scrapers run in parallel; each site failure is isolated.
- `pokevolt` uses `https://www.pokevolt.shop`.
- `toysonfire` uses `https://www.toysonfire.ca`.
- Some targets (for example TCGPlayer/Cardmarket) may still require browser automation or geo/session tuning for full coverage.
- Current implementation is designed for safe iteration and architecture, not anti-bot bypassing.
