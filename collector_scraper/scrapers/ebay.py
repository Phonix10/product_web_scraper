from collector_scraper.core.generic_html_scraper import GenericListScraper


class EbayScraper(GenericListScraper):
    source = "ebay"
    base_url = "https://www.ebay.com"
    search_url_template = "https://www.ebay.com/sch/i.html?_nkw={query}"
    item_selector = ".srp-results .s-item"
    title_selectors = (".s-item__title",)
    price_selectors = (".s-item__price",)
    link_selectors = (".s-item__link",)
    blocked_title_keywords = ("shop on ebay",)
