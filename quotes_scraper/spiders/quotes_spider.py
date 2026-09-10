"""Spider that crawls https://quotes.toscrape.com.

quotes.toscrape.com is a sandbox site published by Scrapinghub/Zyte
specifically for people to practice and demo scraping against, which makes
it a safe, no-permission-needed target for a "hello world" Scrapy example.

Run it with:

    scrapy crawl quotes -O quotes.jsonl

The `-O` flag overwrites the output file with newline-delimited JSON;
use `-o` to append instead.
"""

from __future__ import annotations

from collections.abc import Iterable

import scrapy
from scrapy.http import Response
from scrapy.loader import ItemLoader

from quotes_scraper.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response: Response) -> Iterable[QuoteItem | scrapy.Request]:
        """Parse a listing page: yield one item per quote, then follow
        the "Next" pagination link if present."""
        for quote in response.css("div.quote"):
            loader = ItemLoader(item=QuoteItem(), selector=quote)
            loader.add_css("text", "span.text::text")
            loader.add_css("author", "small.author::text")
            loader.add_css("tags", "div.tags a.tag::text")
            loader.add_value("source_url", response.url)
            yield loader.load_item()

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
