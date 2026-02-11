from collector_scraper.core.generic_html_scraper import GenericListScraper


class EbayScraper(GenericListScraper):
    source = "ebay"
    base_url = "https://www.ebay.com"
    connect_timeout_seconds = 8
    read_timeout_seconds = 18
    search_url_template = "https://www.ebay.com/sch/i.html?_nkw={query}&_ipg=60"
    fallback_search_url_templates = (
        "https://www.ebay.com/sch/i.html?_nkw={query}&_sop=12&_ipg=60",
    )
    item_selector = ".srp-results .s-item"
    title_selectors = ("h3.s-item__title", ".s-item__title")
    price_selectors = (".s-item__price", ".s-item__detail .s-item__price")
    link_selectors = (".s-item__link",)
    blocked_title_keywords = (
        "shop on ebay",
        "shop with confidence",
        "new listing",
    )
