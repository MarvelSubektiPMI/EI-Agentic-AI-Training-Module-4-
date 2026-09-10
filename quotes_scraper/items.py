"""Item definitions for the quotes_scraper project.

Items are Scrapy's typed containers for scraped data. Keeping field
definitions here (rather than passing around raw dicts) gives us:

  * a single source of truth for the scraped schema
  * cheap validation/normalization via input/output processors
  * easy serialization to JSON/CSV via Scrapy's built-in exporters

See: https://docs.scrapy.org/en/latest/topics/items.html
"""

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


def strip_text(value: str) -> str:
    """Trim whitespace left over after tag removal."""
    return value.strip()


def strip_author_prefix(value: str) -> str:
    """Quotes.toscrape prefixes some author links with '(about)'; drop it."""
    return value.replace("(about)", "").strip()


class QuoteItem(scrapy.Item):
    """A single quote scraped from https://quotes.toscrape.com."""

    # MapCompose runs each function in order over every extracted value;
    # TakeFirst keeps only the first (we only ever expect one match per field).
    text = scrapy.Field(
        input_processor=MapCompose(remove_tags, strip_text),
        output_processor=TakeFirst(),
    )
    author = scrapy.Field(
        input_processor=MapCompose(remove_tags, strip_author_prefix),
        output_processor=TakeFirst(),
    )
    tags = scrapy.Field(
        input_processor=MapCompose(strip_text),
        # keep the full list of tags rather than collapsing to one value
    )
    source_url = scrapy.Field(output_processor=TakeFirst())
