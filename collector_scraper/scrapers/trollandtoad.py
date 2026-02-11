from collector_scraper.core.generic_html_scraper import GenericListScraper


class TrollAndToadScraper(GenericListScraper):
    source = "trollandtoad"
    base_url = "https://www.trollandtoad.com"
    search_url_template = "https://www.trollandtoad.com/search?search-words={query}"
    item_selector = ".search-result, .product-card, .product-result"
    title_selectors = (
        "a.search-result-title",
        ".product-card__title",
        "a[href*='/p']",
    )
    price_selectors = (
        ".search-result-price",
        ".product-card__price",
        ".price",
    )
    link_selectors = (
        "a.search-result-title",
        "a[href*='/p']",
    )
