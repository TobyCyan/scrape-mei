"""
Kotobukiya scraper implementation.
"""
from typing import List
from urllib.parse import urljoin
from .base_scraper import BaseScraper


class KotobukiyaScraper(BaseScraper):
    """
    Scraper for Kotobukiya product pages.
    
    Example URL patterns:
    - https://en.kotobukiya.co.jp/product/...
    - https://www.kotobukiya.co.jp/product/...
    """
    
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
            'div.product-image img',
            'div.productImage img',
            'div.slider img',
            'div.gallery img',
            'ul.product-images img',
            'div.images img',
        ]
        
        for selector in gallery_selectors:
            images = self.soup.select(selector)
            if images:
                for img in images:
                    src = img.get('src') or img.get('data-src') or img.get('data-zoom-image')
                    if src:
                        full_url = urljoin(self.url, src)
                        # Skip thumbnails
                        if 'thumb' not in full_url.lower():
                            if full_url not in image_urls:
                                image_urls.append(full_url)
                break
        
        # Strategy 2: Look for high-res image links
        if not image_urls:
            image_links = self.soup.find_all('a', href=True)
            for link in image_links:
                href = link.get('href')
                if href and any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    full_url = urljoin(self.url, href)
                    if full_url not in image_urls:
                        image_urls.append(full_url)
        
        # Strategy 3: Find all relevant images on page
        if not image_urls:
            all_images = self.soup.find_all('img')
            for img in all_images:
                src = img.get('src') or img.get('data-src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    # Filter out icons, logos, banners
                    if not any(word in src.lower() for word in ['icon', 'logo', 'banner', 'nav', 'menu']):
                        full_url = urljoin(self.url, src)
                        if full_url not in image_urls:
                            image_urls.append(full_url)
        
        self.logger.info(f"Found {len(image_urls)} images for Kotobukiya product")
        return image_urls
