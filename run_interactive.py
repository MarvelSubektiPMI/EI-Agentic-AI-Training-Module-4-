#!/usr/bin/env python3
"""Interactive front-end for GenericSpider.

Prompts you for a target URL and the CSS selectors you want scraped, then
runs a Scrapy crawl in-process and writes the results to a file. This is
the easiest way to point this project at a site other than
quotes.toscrape.com without writing any code.

Usage:
    python run_interactive.py

Run it from the repository root (where scrapy.cfg lives) so the project's
settings (throttling, robots.txt compliance, etc.) are picked up.
"""

from __future__ import annotations

import json
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from quotes_scraper.spiders.generic_spider import GenericSpider


def _prompt(message: str, *, required: bool = True, default: str | None = None) -> str:
    while True:
        raw = input(message).strip()
        if raw:
            return raw
        if default is not None:
            return default
        if not required:
            return ""
        print("  -> this value is required, please try again.")


def _collect_fields() -> dict[str, str]:
    print(
        "\nNow define the fields to extract from each item. For every one, "
        "give it a name and a CSS selector (scoped inside one item element).\n"
        "Tip: append '[]' to a selector to collect ALL matches instead of "
        "just the first (e.g. 'a.tag::text[]' for a list of tags).\n"
        "Press Enter with a blank name when you're done adding fields.\n"
    )
    fields: dict[str, str] = {}
    while True:
        name = input(f"  Field #{len(fields) + 1} name (blank to finish): ").strip()
        if not name:
            if fields:
                return fields
            print("  -> add at least one field before finishing.")
            continue
        selector = _prompt(f"    CSS selector for '{name}': ")
        fields[name] = selector


def _feed_format_for(path: str) -> str:
    if path.endswith(".csv"):
        return "csv"
    if path.endswith((".jsonl", ".jl")):
        return "jsonlines"
    return "json"


def main() -> None:
    print("=== Scrapy generic spider: interactive setup ===\n")

    start_url = _prompt("Start URL (e.g. https://example.com/products): ")
    item_selector = _prompt(
        "CSS selector matching ONE element per item to scrape "
        "(e.g. 'div.product', 'article.post', 'div.quote'): "
    )
    fields = _collect_fields()
    next_page_selector = _prompt(
        "\nCSS selector for the 'next page' link's href, or leave blank if "
        "there's no pagination (e.g. 'a.next::attr(href)'): ",
        required=False,
    )
    allowed_domains = _prompt(
        "Comma-separated allowed domain(s) to restrict the crawl to, or "
        "leave blank to allow any domain reachable from the start URL: ",
        required=False,
    )
    output_path = _prompt(
        "Output file to write results to (.json / .jsonl / .csv): ",
        required=False,
        default="output.jsonl",
    )

    settings = get_project_settings()
    settings.set("FEEDS", {output_path: {"format": _feed_format_for(output_path)}})

    print(f"\nStarting crawl -> writing results to {output_path} ...\n")

    process = CrawlerProcess(settings)
    process.crawl(
        GenericSpider,
        start_url=start_url,
        item_selector=item_selector,
        fields=json.dumps(fields),
        next_page_selector=next_page_selector or None,
        allowed_domains=allowed_domains or None,
    )
    process.start()  # blocks until the crawl finishes

    print(f"\nDone. Results written to: {output_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
