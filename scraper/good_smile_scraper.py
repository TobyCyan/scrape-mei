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
        
        # Strategy 1: Find images in product gallery (specific containers)
        gallery_selectors = [
            'div.itemImg img',
            'div.product-gallery img',
            'div.gallery img',
            'div.slider img',
            'ul.slides img',
            'div.product-images img',
        ]
        
        for selector in gallery_selectors:
            images = self.soup.select(selector)
            if images:
                for img in images:
                    src = img.get('src') or img.get('data-src') or img.get('data-original')
                    if src:
                        full_url = urljoin(self.url, src)
                        # Skip thumbnails, small images, and non-product images
                        if not any(word in full_url.lower() for word in ['thumb', 'small', 'icon', 'logo', 'banner', 'btn', 'button', 'nav']):
                            if full_url not in image_urls:
                                image_urls.append(full_url)
                if image_urls:
                    break
        
        # Strategy 2: Look for high-resolution image links (fallback)
        if not image_urls:
            image_links = self.soup.find_all('a', href=True)
            for link in image_links:
                href = link.get('href')
                if href and any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    # Only include if it's clearly a product image
                    if any(word in href.lower() for word in ['product', 'item', 'figure', 'img']):
                        full_url = urljoin(self.url, href)
                        if full_url not in image_urls:
                            image_urls.append(full_url)
        
        self.logger.info(f"Found {len(image_urls)} images for Good Smile product")
        return image_urls
