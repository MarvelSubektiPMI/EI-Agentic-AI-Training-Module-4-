"""Unit tests for QuotesSpider.parse().

These tests feed a local HTML fixture into the spider's callback so they
run fully offline (no network access, no dependency on the live site) -
the recommended pattern for testing Scrapy spider parsing logic.
"""

from pathlib import Path

import pytest
from scrapy.http import HtmlResponse, Request

from quotes_scraper.spiders.quotes_spider import QuotesSpider

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "quotes_page.html"


def _fake_response(url: str = "https://quotes.toscrape.com/") -> HtmlResponse:
    body = FIXTURE_PATH.read_bytes()
    return HtmlResponse(url=url, request=Request(url=url), body=body, encoding="utf-8")


@pytest.fixture
def spider() -> QuotesSpider:
    return QuotesSpider()


def test_parse_extracts_all_quotes(spider: QuotesSpider) -> None:
    results = list(spider.parse(_fake_response()))
    items = [r for r in results if not isinstance(r, Request)]
    assert len(items) == 2


def test_parse_extracts_expected_fields(spider: QuotesSpider) -> None:
    results = list(spider.parse(_fake_response()))
    items = [r for r in results if not isinstance(r, Request)]

    first = items[0]
    assert first["author"] == "Albert Einstein"
    assert "world as we have created it" in first["text"]
    assert first["tags"] == ["change", "deep-thoughts"]
    assert first["source_url"] == "https://quotes.toscrape.com/"


def test_parse_follows_pagination_link(spider: QuotesSpider) -> None:
    results = list(spider.parse(_fake_response()))
    requests = [r for r in results if isinstance(r, Request)]

    assert len(requests) == 1
    assert requests[0].url == "https://quotes.toscrape.com/page/2/"
