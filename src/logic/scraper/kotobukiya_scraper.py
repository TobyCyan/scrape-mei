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
        
        # Try multiple strategies in order of preference
        strategies = [
            self._extract_from_gallery_selectors,
            self._extract_from_image_links,
            self._extract_from_all_images,
        ]
        
        for strategy in strategies:
            image_urls = strategy()
            if image_urls:
                # Convert thumbnail URLs to full-resolution URLs
                image_urls = [self._convert_to_full_resolution(url) for url in image_urls]
                self.logger.info(f"Found {len(image_urls)} images for Kotobukiya product")
                return image_urls
        
        self.logger.warning("No images found for Kotobukiya product")
        return []
    
    def _extract_from_gallery_selectors(self) -> List[str]:
        """Extract images from product gallery/slider using CSS selectors."""
        image_urls = []
        gallery_selectors = [
            'div.detailSlider img',
            'div.detailHeader_main img',
            'div.detailHeader_inner img',
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
            if not images:
                continue
            
            for img in images:
                src = img.get('src') or img.get('data-src') or img.get('data-zoom-image')
                if not src:
                    continue
                
                full_url = urljoin(self.url, src)
                
                if not self._is_product_image(full_url):
                    continue
                
                if full_url not in image_urls:
                    image_urls.append(full_url)
            
            if image_urls:
                break
        
        return image_urls
    
    def _extract_from_image_links(self) -> List[str]:
        """Extract high-res image URLs from anchor tags."""
        image_urls = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        for link in self.soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue
            
            # Check if link points to an image
            if not any(ext in href.lower() for ext in image_extensions):
                continue
            
            # Only include product-related images
            if not any(word in href.lower() for word in ['product', 'item', 'figure', 'img']):
                continue
            
            full_url = urljoin(self.url, href)
            if full_url not in image_urls:
                image_urls.append(full_url)
        
        return image_urls
    
    def _extract_from_all_images(self) -> List[str]:
        """Last resort: find all relevant images on page."""
        image_urls = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        for img in self.soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            
            # Check if src has image extension
            if not any(ext in src.lower() for ext in image_extensions):
                continue
            
            # Only include product-related images
            if not any(word in src.lower() for word in ['product', 'item', 'figure']):
                continue
            
            if not self._is_product_image(src):
                continue
            
            full_url = urljoin(self.url, src)
            if full_url not in image_urls:
                image_urls.append(full_url)
        
        return image_urls
    
    def _is_product_image(self, url: str) -> bool:
        """Check if a URL is likely a product image (not UI element or social media)."""
        excluded_patterns = [
            '_thumb.', '-thumb.', '/thumb.', 'thumb_', 'thumb-',
            'icon', 'logo', 'banner', 'nav', 'menu', 'btn',
            'sns', 'twitter', 'facebook', 'instagram', 'social', 'share',
            'footer', 'header', 'sidebar', 'shop_offer'
        ]
        return not any(pattern in url.lower() for pattern in excluded_patterns)
    
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
