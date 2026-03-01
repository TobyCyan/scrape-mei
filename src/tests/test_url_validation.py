"""
Test URL validation for scrapers.
"""
import sys
import unittest
from pathlib import Path

# Add logic directory to path
logic_path = Path(__file__).parent.parent / 'logic'
sys.path.insert(0, str(logic_path))

from scraper import ScraperFactory


class TestURLValidation(unittest.TestCase):
    """Test cases for URL validation."""
    
    def test_good_smile_valid_urls(self):
        """Test that Good Smile scraper accepts valid Good Smile URLs."""
        valid_urls = [
            'https://www.goodsmile.info/en/product/12345',
            'https://www.goodsmileus.com/products/test',
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                scraper = ScraperFactory.get_scraper('Good Smile', url)
                self.assertIsNotNone(scraper)
    
    def test_good_smile_invalid_urls(self):
        """Test that Good Smile scraper rejects invalid URLs."""
        with self.assertRaises(ValueError):
            ScraperFactory.get_scraper('Good Smile', 'https://www.kotobukiya.co.jp/product/test')
    
    def test_kotobukiya_valid_urls(self):
        """Test that Kotobukiya scraper accepts valid Kotobukiya URLs."""
        valid_urls = [
            'https://en.kotobukiya.co.jp/product/12345',
            'https://www.kotobukiya.co.jp/product/test',
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                scraper = ScraperFactory.get_scraper('Kotobukiya', url)
                self.assertIsNotNone(scraper)
    
    def test_kotobukiya_invalid_urls(self):
        """Test that Kotobukiya scraper rejects invalid URLs."""
        with self.assertRaises(ValueError):
            ScraperFactory.get_scraper('Kotobukiya', 'https://www.goodsmile.info/en/product/test')


if __name__ == "__main__":
    unittest.main(verbosity=2)
