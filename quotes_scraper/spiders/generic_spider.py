"""A generic, user-configurable spider.

Unlike QuotesSpider (hard-coded for quotes.toscrape.com), this spider takes
its target URL and CSS selectors as *run-time arguments*, so it can scrape a
different site's listing pages without touching any code.

Run it directly with Scrapy's `-a` argument syntax:

    scrapy crawl generic \\
        -a start_url="https://quotes.toscrape.com/" \\
        -a item_selector="div.quote" \\
        -a fields='{"text": "span.text::text", "author": "small.author::text", "tags": "a.tag::text[]"}' \\
        -a next_page_selector="li.next a::attr(href)" \\
        -O output.jsonl

`fields` is a JSON object mapping your chosen field name -> a CSS selector
(scoped to each matched item element). Append "[]" to a selector to collect
*all* matches for that field instead of just the first one (e.g. for a list
of tags).

For a friendlier, prompt-driven experience instead of typing all of the
above by hand, run `python run_interactive.py` from the repository root.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

import scrapy
from scrapy.http import Response
from scrapy.selector import Selector


class GenericSpider(scrapy.Spider):
    """Scrape arbitrary listing pages using selectors supplied at run time."""

    name = "generic"

    # This spider's item shape is unknown ahead of time, so the project-wide
    # pipelines (which assume quote-shaped items with "text"/"author") don't
    # apply here — disable them for this spider only.
    custom_settings = {"ITEM_PIPELINES": {}}

    def __init__(
        self,
        start_url: str | None = None,
        item_selector: str | None = None,
        fields: str | None = None,
        next_page_selector: str | None = None,
        allowed_domains: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        if not start_url:
            raise ValueError(
                "Missing required argument: start_url "
                '(e.g. -a start_url="https://example.com")'
            )
        if not item_selector:
            raise ValueError(
                "Missing required argument: item_selector "
                "(a CSS selector matching one element per scraped item, "
                'e.g. -a item_selector="div.product")'
            )
        if not fields:
            raise ValueError(
                "Missing required argument: fields "
                "(a JSON object mapping field name -> CSS selector, e.g. "
                "-a fields='{\"title\": \"h2::text\", \"price\": \".price::text\"}')"
            )

        try:
            parsed_fields = json.loads(fields)
        except json.JSONDecodeError as exc:
            raise ValueError(f"fields must be valid JSON: {exc}") from exc
        if not isinstance(parsed_fields, dict) or not parsed_fields:
            raise ValueError("fields must be a non-empty JSON object")

        self.field_selectors: dict[str, str] = parsed_fields
        self.start_urls = [start_url]
        self.item_selector = item_selector
        self.next_page_selector = next_page_selector

        if allowed_domains:
            self.allowed_domains = [d.strip() for d in allowed_domains.split(",")]

    def parse(self, response: Response) -> Iterable[dict | scrapy.Request]:
        """Extract one dict per matched item, then follow pagination."""
        for element in response.css(self.item_selector):
            item = {
                name: self._extract(element, selector)
                for name, selector in self.field_selectors.items()
            }
            item["source_url"] = response.url
            yield item

        if self.next_page_selector:
            next_page = response.css(self.next_page_selector).get()
            if next_page:
                yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _extract(element: Selector, selector: str) -> str | list[str] | None:
        """Apply a field's CSS selector, honoring a trailing '[]' to mean
        "collect every match" instead of just the first one."""
        if selector.endswith("[]"):
            return element.css(selector[:-2]).getall()
        return element.css(selector).get()
