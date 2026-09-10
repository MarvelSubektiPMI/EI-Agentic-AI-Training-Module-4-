"""Item pipelines for the quotes_scraper project.

Pipelines run after the spider yields an item, in the order set by
ITEM_PIPELINES in settings.py. Splitting concerns into small pipelines
(validate -> dedupe -> persist) keeps each one simple and testable.

See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.spiders import Spider


class ValidationPipeline:
    """Drop items missing required fields instead of letting bad data
    through to storage."""

    REQUIRED_FIELDS = ("text", "author")

    def process_item(self, item, spider: Spider):
        adapter = ItemAdapter(item)
        missing = [f for f in self.REQUIRED_FIELDS if not adapter.get(f)]
        if missing:
            raise DropItem(f"Missing required field(s) {missing}: {item!r}")
        return item


class DuplicatesPipeline:
    """Drop quotes we've already seen in this crawl (some quotes repeat
    across pages on the demo site)."""

    def __init__(self) -> None:
        self.seen_quotes: set[tuple[str, str]] = set()

    def process_item(self, item, spider: Spider):
        adapter = ItemAdapter(item)
        fingerprint = (adapter.get("author"), adapter.get("text"))
        if fingerprint in self.seen_quotes:
            raise DropItem(f"Duplicate quote dropped: {fingerprint}")
        self.seen_quotes.add(fingerprint)
        return item
