from collector_scraper.core.generic_html_scraper import GenericListScraper


class CardmarketScraper(GenericListScraper):
    source = "cardmarket"
    base_url = "https://www.cardmarket.com"
    search_url_template = (
        "https://www.cardmarket.com/en/Pokemon/Products/Search?searchString={query}"
    )
    item_selector = ".table-body .row, .product-row"
    title_selectors = (
        "a[href*='/Products/']",
        ".product-row-name",
        ".col-product a",
    )
    price_selectors = (
        ".price-container",
        ".col-price",
        ".price",
    )
    link_selectors = ("a[href*='/Products/']",)
