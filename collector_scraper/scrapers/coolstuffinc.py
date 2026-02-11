from collector_scraper.core.generic_html_scraper import GenericListScraper


class CoolStuffIncScraper(GenericListScraper):
    source = "coolstuffinc"
    base_url = "https://www.coolstuffinc.com"
    search_url_template = (
        "https://www.coolstuffinc.com/main_search.php?pa=searchOnName&page=1&q={query}"
    )
    item_selector = ".prod_box, .search_result, .product-list-item"
    title_selectors = (
        ".prod_name a",
        ".product-list-item__name",
        "a[href*='/p/']",
    )
    price_selectors = (
        ".regular_price",
        ".product-list-item__price",
        ".price",
    )
    link_selectors = (
        ".prod_name a",
        "a[href*='/p/']",
    )
