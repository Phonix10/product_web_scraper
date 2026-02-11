from collector_scraper.core.generic_html_scraper import GenericListScraper


class CardmarketScraper(GenericListScraper):
    source = "cardmarket"
    base_url = "https://www.cardmarket.com"
    search_url_template = (
        "https://www.cardmarket.com/en/Pokemon/Products/Search?searchString={query}"
    )
    fallback_search_url_templates = (
        "https://www.cardmarket.com/en/Pokemon/Products/Search?searchString={query}&mode=list",
    )
    item_selector = ".table-body .row, .product-row, .article-row"
    title_selectors = (
        "a[href*='/Products/']",
        ".product-row-name",
        ".col-product a",
        ".article-name a",
    )
    price_selectors = (
        ".price-container",
        ".col-price",
        ".price",
        ".article-price",
    )
    link_selectors = ("a[href*='/Products/']",)
