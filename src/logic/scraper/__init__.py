"""
Scraper package for anime figurine image scraping.
"""
from .base_scraper import BaseScraper
from .good_smile_scraper import GoodSmileScraper
from .kotobukiya_scraper import KotobukiyaScraper
from .scraper_factory import ScraperFactory

__all__ = [
    'BaseScraper',
    'GoodSmileScraper',
    'KotobukiyaScraper',
    'ScraperFactory',
]
