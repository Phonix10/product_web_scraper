from collector_scraper.core.shopify_scraper import ShopifyPredictiveScraper


class PokedexScraper(ShopifyPredictiveScraper):
    source = "pokedex"
    base_url = "https://pokedex.in"
    max_items = 80
    fallback_html_templates = (
        "https://pokedex.in/search?q={query}&type=product",
        "https://pokedex.in/search?q={query}",
    )
