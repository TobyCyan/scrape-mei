"""
Kotobukiya scraper implementation.
"""
from typing import List
from urllib.parse import urljoin
import re
from .base_scraper import BaseScraper


class KotobukiyaScraper(BaseScraper):
    """
    Scraper for Kotobukiya product pages.
    
    Example URL patterns:
    - https://en.kotobukiya.co.jp/product/...
    - https://www.kotobukiya.co.jp/product/...
    """
    
    VALID_DOMAINS = [
        'kotobukiya.co.jp',
    ]
    
    def get_product_name(self) -> str:
        """
        Extract product name from Kotobukiya page.
        
        Returns:
            Product name string
        """
        if not self.soup:
            raise ValueError("Page not fetched. Call fetch_page() first.")
        
        # Try multiple selectors for product name
        selectors = [
            'h1.product-name',
            'h1.productName',
            'div.product-title h1',
            'h1.title',
            'h1',
            'div.itemName',
        ]
        
        for selector in selectors:
            element = self.soup.select_one(selector)
            if element and element.get_text(strip=True):
                name = element.get_text(strip=True)
                self.logger.info(f"Found product name: {name}")
                return name
        
        # Fallback to page title
        title_tag = self.soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True).split('|')[0].strip()
        
        self.logger.warning("Could not find product name, using default")
        return "unknown_kotobukiya_product"
    
    def get_image_urls(self) -> List[str]:
        """
        Extract all product image URLs from Kotobukiya page.
        
        Returns:
            List of full image URLs
        """
        if not self.soup:
            raise ValueError("Page not fetched. Call fetch_page() first.")
        
        image_urls = []
        
        # Strategy 1: Find images in product gallery/slider
        gallery_selectors = [
            'div.detailSlider img',                # Kotobukiya main slider
            'div.detailHeader_main img',           # Kotobukiya header main
            'div.detailHeader_inner img',          # Kotobukiya header inner
            'div.product-image img',
            'div.productImage img',
            'div.slider img',
            'div.gallery img',
            'ul.product-images img',
            'div.product-gallery img',
            'div.images img',
        ]
        
        for selector in gallery_selectors:
            images = self.soup.select(selector)
            if images:
                for img in images:
                    src = img.get('src') or img.get('data-src') or img.get('data-zoom-image')
                    if src:
                        full_url = urljoin(self.url, src)
                        # Skip social media icons, shop offers, and non-product images
                        # Note: Use word boundaries to avoid filtering 'thumbnail' directory paths
                        excluded_patterns = [
                            '_thumb.', '-thumb.', '/thumb.', 'thumb_', 'thumb-',  # Actual thumbnails
                            'icon', 'logo', 'banner', 'nav', 'menu', 'btn',
                            'sns', 'twitter', 'facebook', 'instagram', 'social', 'share',
                            'footer', 'header', 'sidebar', 'shop_offer'  # Shop offers return 403
                        ]
                        if not any(pattern in full_url.lower() for pattern in excluded_patterns):
                            if full_url not in image_urls:
                                image_urls.append(full_url)
                if image_urls:
                    break
        
        # Strategy 2: Look for high-res image links
        if not image_urls:
            image_links = self.soup.find_all('a', href=True)
            for link in image_links:
                href = link.get('href')
                if href and any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    # Only include if it looks like a product image
                    if any(word in href.lower() for word in ['product', 'item', 'figure', 'img']):
                        full_url = urljoin(self.url, href)
                        if full_url not in image_urls:
                            image_urls.append(full_url)
        
        # Strategy 3: Find all relevant images on page (last resort)
        if not image_urls:
            all_images = self.soup.find_all('img')
            for img in all_images:
                src = img.get('src') or img.get('data-src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    # Only include product-related images, filter out UI elements and social media
                    if any(word in src.lower() for word in ['product', 'item', 'figure']):
                        excluded_patterns = [
                            '_thumb.', '-thumb.', '/thumb.', 'thumb_', 'thumb-',  # Actual thumbnails
                            'icon', 'logo', 'banner', 'nav', 'menu', 'btn',
                            'sns', 'twitter', 'facebook', 'instagram', 'social', 'share',
                            'footer', 'header', 'sidebar', 'shop_offer'  # Shop offers return 403
                        ]
                        if not any(pattern in src.lower() for pattern in excluded_patterns):
                            full_url = urljoin(self.url, src)
                            if full_url not in image_urls:
                                image_urls.append(full_url)
        
        # Convert thumbnail URLs to full-resolution URLs
        image_urls = [self._convert_to_full_resolution(url) for url in image_urls]
        
        self.logger.info(f"Found {len(image_urls)} images for Kotobukiya product")
        return image_urls
    
    def _convert_to_full_resolution(self, url: str) -> str:
        """
        Convert Kotobukiya thumbnail proxy URLs to full-resolution URLs.
        
        Kotobukiya serves images through a thumbnail proxy like:
        /sm_files_thumbnail/co/product/.../image.jpg/200.jpg
        
        The full-resolution version is:
        /sm_files/co/product/.../image.jpg
        
        Args:
            url: Thumbnail URL
            
        Returns:
            Full-resolution URL
        """
        # Replace thumbnail path with full path
        url = url.replace('/sm_files_thumbnail/', '/sm_files/')
        
        # Remove size suffix (e.g., /200.jpg, /1000.jpg) at the end
        # Pattern: ends with /digits.extension
        url = re.sub(r'/\d+\.(jpg|jpeg|png|webp)$', '', url, flags=re.IGNORECASE)
        
        return url
