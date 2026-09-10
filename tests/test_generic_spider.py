"""Unit tests for GenericSpider.

Exercises the spider entirely offline against a local HTML fixture — same
pattern as test_quotes_spider.py.
"""

import json
from pathlib import Path

import pytest
from scrapy.http import HtmlResponse, Request

from quotes_scraper.spiders.generic_spider import GenericSpider

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "generic_page.html"


def _fake_response(url: str = "https://example.com/products") -> HtmlResponse:
    body = FIXTURE_PATH.read_bytes()
    return HtmlResponse(url=url, request=Request(url=url), body=body, encoding="utf-8")


def _make_spider(**overrides) -> GenericSpider:
    kwargs = {
        "start_url": "https://example.com/products",
        "item_selector": "div.product",
        "fields": json.dumps(
            {
                "title": "h2.title::text",
                "price": "span.price::text",
                "tags": "a.tag::text[]",
            }
        ),
        "next_page_selector": "a.next::attr(href)",
    }
    kwargs.update(overrides)
    return GenericSpider(**kwargs)


def test_requires_start_url() -> None:
    with pytest.raises(ValueError, match="start_url"):
        GenericSpider(item_selector="div.product", fields="{}")


def test_requires_item_selector() -> None:
    with pytest.raises(ValueError, match="item_selector"):
        GenericSpider(start_url="https://example.com", fields="{}")


def test_requires_fields() -> None:
    with pytest.raises(ValueError, match="fields"):
        GenericSpider(start_url="https://example.com", item_selector="div.product")


def test_rejects_invalid_fields_json() -> None:
    with pytest.raises(ValueError, match="valid JSON"):
        GenericSpider(
            start_url="https://example.com",
            item_selector="div.product",
            fields="not-json",
        )


def test_parse_extracts_configured_fields() -> None:
    spider = _make_spider()
    results = list(spider.parse(_fake_response()))
    items = [r for r in results if not isinstance(r, Request)]

    assert len(items) == 2
    assert items[0] == {
        "title": "Widget A",
        "price": "$9.99",
        "tags": ["tools", "sale"],
        "source_url": "https://example.com/products",
    }
    assert items[1]["title"] == "Widget B"
    assert items[1]["tags"] == ["gadgets"]


def test_parse_follows_pagination() -> None:
    spider = _make_spider()
    results = list(spider.parse(_fake_response()))
    requests = [r for r in results if isinstance(r, Request)]

    assert len(requests) == 1
    assert requests[0].url == "https://example.com/products/page/2/"


def test_allowed_domains_parsed_from_comma_separated_string() -> None:
    spider = _make_spider(allowed_domains="example.com, cdn.example.com")
    assert spider.allowed_domains == ["example.com", "cdn.example.com"]
