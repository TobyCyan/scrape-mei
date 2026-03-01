"""
Test to verify bug fixes work correctly.
"""
import sys
import unittest
from pathlib import Path

# Add logic directory to path
logic_path = Path(__file__).parent.parent / 'logic'
sys.path.insert(0, str(logic_path))

from scraper import ScraperFactory


class TestBugFixes(unittest.TestCase):
    """Test cases for verifying bug fixes."""
    
    def test_factory_no_duplicates(self):
        """Test that factory doesn't return duplicate companies."""
        companies = ScraperFactory.get_supported_companies()
        
        # Check for duplicates
        self.assertEqual(len(companies), len(set(companies)),
                        "Duplicate companies found in factory")
        
        # Check that Good Smile only appears once
        good_smile_count = sum(1 for c in companies if 'good' in c.lower() and 'smile' in c.lower())
        self.assertEqual(good_smile_count, 1,
                        f"Good Smile appears {good_smile_count} times (should be 1)")
    
    def test_aliases(self):
        """Test that company aliases work correctly."""
        test_cases = [
            ('Good Smile', 'GoodSmileScraper', 'https://www.goodsmile.info/en/product/test'),
            ('good smile', 'GoodSmileScraper', 'https://www.goodsmile.info/en/product/test'),
            ('goodsmile', 'GoodSmileScraper', 'https://www.goodsmileus.com/products/test'),
            ('good_smile', 'GoodSmileScraper', 'https://www.goodsmileus.com/products/test'),
        ]
        
        for company_name, expected_class, test_url in test_cases:
            with self.subTest(company=company_name):
                scraper = ScraperFactory.get_scraper(company_name, test_url)
                self.assertEqual(scraper.__class__.__name__, expected_class,
                               f"'{company_name}' should return {expected_class}")
    
    def test_dpi_awareness(self):
        """Test that DPI awareness code doesn't crash."""
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            # Not available on non-Windows platforms, which is OK
            self.skipTest("DPI awareness not available (non-Windows platform)")


if __name__ == '__main__':
    unittest.main(verbosity=2)
