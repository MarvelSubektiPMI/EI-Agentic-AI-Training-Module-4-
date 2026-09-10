# quotes_scraper — Scrapy Web Scraping Example

A small, production-style [Scrapy](https://www.scrapy.org/) project that
scrapes quotes, authors, and tags from
[quotes.toscrape.com](https://quotes.toscrape.com) — a sandbox site built
specifically for people to practice scraping against, so it's a safe target
for a demo with no permission concerns.

It's meant as a reference for how to structure a real Scrapy project rather
than a single throwaway script: typed `Item`s, an `ItemLoader` with
input/output processors for cleaning, a small pipeline chain for
validation/deduplication, polite crawling settings, and offline unit tests.

## Project layout

```
scrapy.cfg                       # Scrapy project entry point
requirements.txt
quotes_scraper/
├── settings.py                  # crawl politeness, pipelines, caching, retries
├── items.py                     # QuoteItem: schema + cleaning processors
├── pipelines.py                 # ValidationPipeline, DuplicatesPipeline
└── spiders/
    └── quotes_spider.py         # QuotesSpider: crawl + pagination logic
tests/
├── fixtures/quotes_page.html    # offline HTML fixture for the spider test
└── test_quotes_spider.py        # parses the fixture, no network required
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the spider

From the repository root (where `scrapy.cfg` lives):

```bash
# Write results as newline-delimited JSON (overwrites the file each run)
scrapy crawl quotes -O quotes.jsonl

# Or as CSV
scrapy crawl quotes -O quotes.csv

# Limit the crawl for a quick smoke test
scrapy crawl quotes -O quotes.jsonl -s CLOSESPIDER_ITEMCOUNT=10
```

Each output record looks like:

```json
{
  "text": "The world as we have created it is a process of our thinking.",
  "author": "Albert Einstein",
  "tags": ["change", "deep-thoughts"],
  "source_url": "https://quotes.toscrape.com/"
}
```

## Running the tests

```bash
pytest -v
```

Tests feed a saved HTML fixture straight into `QuotesSpider.parse()`, so they
run fully offline and don't depend on the live site being reachable.

## Best practices applied here

- **Respect the target site.** `ROBOTSTXT_OBEY = True`, a throttled
  `DOWNLOAD_DELAY` + `AUTOTHROTTLE`, a bounded `CONCURRENT_REQUESTS_PER_DOMAIN`,
  and an honest `USER_AGENT` — no spoofing, no hammering.
- **Typed items over raw dicts** (`items.py`) so the scraped schema is
  documented and validated in one place.
- **`ItemLoader` + processors** for input cleaning (stripping tags/whitespace)
  instead of ad-hoc string munging scattered through the spider.
- **Pipelines for cross-cutting concerns** — validation and de-duplication
  are separate, single-purpose pipeline classes, not inlined in the spider.
- **Resilience**: retries (`RETRY_ENABLED`/`RETRY_TIMES`) for transient
  network errors, and `HTTPCACHE_ENABLED` so repeated local dev runs don't
  re-hit the network.
- **Tests that don't require network access** — a local HTML fixture keeps
  CI fast and deterministic.

## Extending this example

- Add more spiders under `quotes_scraper/spiders/` (one file per site/source).
- Add a storage pipeline (e.g. write to SQLite/Postgres) after
  `DuplicatesPipeline` in `ITEM_PIPELINES`.
- Add `FEEDS` in `settings.py` if you want output configured declaratively
  instead of via the `-O`/`-o` CLI flags.
