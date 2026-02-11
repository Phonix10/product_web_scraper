from collector_scraper.core.shopify_scraper import ShopifyPredictiveScraper


class TrollAndToadScraper(ShopifyPredictiveScraper):
    source = "trollandtoad"
    base_url = "https://www.trollandtoad.com"
    max_items = 60
    fallback_html_templates = (
        "https://www.trollandtoad.com/search?q={query}&type=product",
        "https://www.trollandtoad.com/search?q={query}",
        "https://www.trollandtoad.com/products/search?search_words={query}",
    )
