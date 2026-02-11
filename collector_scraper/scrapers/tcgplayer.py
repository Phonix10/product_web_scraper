from collector_scraper.core.generic_html_scraper import GenericListScraper


class TCGPlayerScraper(GenericListScraper):
    source = "tcgplayer"
    base_url = "https://www.tcgplayer.com"
    search_url_template = "https://www.tcgplayer.com/search/all/product?q={query}"
    item_selector = ".search-result, .product-card"
    title_selectors = (
        ".search-result__title",
        ".product-card__title",
        "a[data-testid='productNameLink']",
    )
    price_selectors = (
        ".inventory__price-with-shipping",
        ".search-result__market-price--value",
        ".product-card__market-price--value",
        "[data-testid='listingPrice']",
    )
    link_selectors = ("a[href*='/product/']",)
