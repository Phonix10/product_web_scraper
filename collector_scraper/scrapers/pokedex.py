from collector_scraper.core.generic_html_scraper import GenericListScraper


class PokedexScraper(GenericListScraper):
    source = "pokedex"
    base_url = "https://pokedex.in"
    search_url_template = "https://pokedex.in/search?q={query}"
    item_selector = ".grid-product, .product-item, .card-wrapper"
    title_selectors = (
        ".grid-product__title",
        ".product-item__title",
        ".card-information__text",
        "a[href*='/products/']",
    )
    price_selectors = (
        ".grid-product__price",
        ".price-item--last",
        ".price",
    )
    link_selectors = ("a[href*='/products/']",)
