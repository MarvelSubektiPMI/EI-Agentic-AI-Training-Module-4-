"""Scrapy settings for the quotes_scraper project.

Only settings that differ from Scrapy's defaults, or that are worth
calling out explicitly, are set here. Full reference:
https://docs.scrapy.org/en/latest/topics/settings.html
"""

BOT_NAME = "quotes_scraper"

SPIDER_MODULES = ["quotes_scraper.spiders"]
NEWSPIDER_MODULE = "quotes_scraper.spiders"

# --- Politeness / good citizenship -----------------------------------------
# Respect robots.txt and throttle ourselves instead of hammering the target.
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1.0
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 4

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Identify ourselves honestly rather than spoofing a browser UA.
USER_AGENT = "quotes_scraper (+https://github.com/MarvelSubektiPMI)"

# --- HTTP caching (speeds up repeated local runs during development) -------
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = "httpcache"

# --- Retries -----------------------------------------------------------------
RETRY_ENABLED = True
RETRY_TIMES = 2

# --- Item pipelines ----------------------------------------------------------
ITEM_PIPELINES = {
    "quotes_scraper.pipelines.ValidationPipeline": 300,
    "quotes_scraper.pipelines.DuplicatesPipeline": 400,
}

# --- Logging -----------------------------------------------------------------
LOG_LEVEL = "INFO"

# Modern async reactor (Scrapy's current default/recommended setting).
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
