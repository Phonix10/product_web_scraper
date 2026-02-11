from collector_scraper.core.generic_html_scraper import GenericListScraper


class ToysOnFireScraper(GenericListScraper):
    source = "toysonfire"
    base_url = "https://www.toysonfire.ca"
    search_url_template = "https://www.toysonfire.ca/shop/search?search={query}"
    fallback_search_url_templates = (
        "https://www.toysonfire.ca/search?search={query}",
        "https://www.toysonfire.ca/shop?q={query}",
        "https://www.toysonfire.ca/shop",
    )
    item_selector = ".product-item, .shop-item, .product-card, .product"
    title_selectors = (
        ".product-item__title",
        ".product-title",
        "a[href*='/shop/product/']",
        "a[href*='/product/']",
    )
    price_selectors = (
        ".product-item__price",
        ".product-price",
        ".price",
        ".money",
    )
    link_selectors = (
        "a[href*='/shop/product/']",
        "a[href*='/product/']",
    )
