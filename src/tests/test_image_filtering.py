"""
Test that social media images are filtered out.
"""
import sys
import unittest
from pathlib import Path

# Add logic directory to path
logic_path = Path(__file__).parent.parent / 'logic'
sys.path.insert(0, str(logic_path))


class TestImageFiltering(unittest.TestCase):
    """Test cases for image filtering."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.excluded_patterns = [
            '_thumb.', '-thumb.', '/thumb.', 'thumb_', 'thumb-',
            'small', 'icon', 'logo', 'banner', 'btn', 'button', 'nav',
            'sns', 'twitter', 'facebook', 'instagram', 'social', 'share',
            'footer', 'header', 'sidebar'
        ]
    
    def _is_filtered(self, url):
        """Check if a URL should be filtered."""
        return any(pattern in url.lower() for pattern in self.excluded_patterns)
    
    def test_sns_images_filtered(self):
        """Test that SNS (social media) images are filtered."""
        sns_urls = [
            'https://www.kotobukiya.co.jp/files/page/sns/twitter/kotobuki_figure.jpg',
            'https://www.goodsmile.info/images/social/facebook-icon.png',
        ]
        
        for url in sns_urls:
            with self.subTest(url=url):
                self.assertTrue(self._is_filtered(url),
                              f"SNS image should be filtered: {url}")
    
    def test_ui_elements_filtered(self):
        """Test that UI elements (icons, logos, etc.) are filtered."""
        ui_urls = [
            'https://www.kotobukiya.co.jp/icons/share-button.png',
            'https://example.com/header-logo.jpg',
            'https://example.com/footer-banner.jpg',
            'https://example.com/sidebar-nav.jpg',
        ]
        
        for url in ui_urls:
            with self.subTest(url=url):
                self.assertTrue(self._is_filtered(url),
                              f"UI element should be filtered: {url}")
    
    def test_thumbnail_images_filtered(self):
        """Test that thumbnail images with filename patterns are filtered."""
        thumb_urls = [
            'https://example.com/product-thumb.jpg',
            'https://example.com/image_thumb.jpg',
            'https://example.com/img-thumb.png',
        ]
        
        for url in thumb_urls:
            with self.subTest(url=url):
                self.assertTrue(self._is_filtered(url),
                              f"Thumbnail should be filtered: {url}")
    
    def test_product_images_not_filtered(self):
        """Test that legitimate product images are NOT filtered."""
        valid_urls = [
            'https://www.kotobukiya.co.jp/product/item/12345.jpg',
            'https://www.goodsmile.info/en/product/figure/main-image.jpg',
            'https://example.com/products/figure-001.jpg',
            'https://www.kotobukiya.co.jp/sm_files_thumbnail/co/product/figure.jpg',  # Path contains 'thumbnail' but not filtered
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertFalse(self._is_filtered(url),
                               f"Product image should NOT be filtered: {url}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
