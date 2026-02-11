from collector_scraper.core.woocommerce_scraper import WooCommerceStoreScraper


class BeyondGamingScraper(WooCommerceStoreScraper):
    source = "beyondgaming"
    base_url = "https://beyondgaming.in"
    per_page = 40
