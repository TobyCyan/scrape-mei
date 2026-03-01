"""
Good Smile Company scraper implementation.
"""
from typing import List
from urllib.parse import urljoin
from .base_scraper import BaseScraper


class GoodSmileScraper(BaseScraper):
    """
    Scraper for Good Smile Company product pages.
    
    Example URL patterns:
    - https://www.goodsmile.info/en/product/...
    - https://www.goodsmileus.com/product/...
    """
    
    def get_product_name(self) -> str:
        """
        Extract product name from Good Smile Company page.
        
        Returns:
            Product name string
        """
        if not self.soup:
            raise ValueError("Page not fetched. Call fetch_page() first.")
        
        # Try multiple selectors for product name
        selectors = [
            'h1.title',
            'h1.product-title',
            'div.itemName',
            'h1',
            'div.product-name',
            'span.product-title',
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
        return "unknown_goodsmile_product"
    
    def get_image_urls(self) -> List[str]:
        """
        Extract all product image URLs from Good Smile Company page.
        
        Returns:
            List of full image URLs
        """
        if not self.soup:
            raise ValueError("Page not fetched. Call fetch_page() first.")
        
        image_urls = []
        
        # Strategy 1: Find images in product gallery
        gallery_selectors = [
            'div.itemImg img',
            'div.product-gallery img',
            'div.gallery img',
            'div.images img',
            'div.product-images img',
        ]
        
        for selector in gallery_selectors:
            images = self.soup.select(selector)
            if images:
                for img in images:
                    src = img.get('src') or img.get('data-src') or img.get('data-original')
                    if src:
                        full_url = urljoin(self.url, src)
                        # Skip thumbnails and small images
                        if 'thumb' not in full_url.lower() and 'small' not in full_url.lower():
                            if full_url not in image_urls:
                                image_urls.append(full_url)
                break
        
        # Strategy 2: Find all images on page if gallery not found
        if not image_urls:
            all_images = self.soup.find_all('img')
            for img in all_images:
                src = img.get('src') or img.get('data-src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    # Filter out icons, logos, banners
                    if not any(word in src.lower() for word in ['icon', 'logo', 'banner', 'btn', 'button']):
                        full_url = urljoin(self.url, src)
                        if full_url not in image_urls:
                            image_urls.append(full_url)
        
        self.logger.info(f"Found {len(image_urls)} images for Good Smile product")
        return image_urls
