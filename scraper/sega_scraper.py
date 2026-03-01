"""
Sega scraper implementation.
"""
from typing import List
from urllib.parse import urljoin
from .base_scraper import BaseScraper


class SegaScraper(BaseScraper):
    """
    Scraper for Sega product pages (Sega Prize figures).
    
    Example URL patterns:
    - https://segaprize.com/prize_item/...
    - https://www.sega.co.jp/toys/...
    """
    
    def get_product_name(self) -> str:
        """
        Extract product name from Sega page.
        
        Returns:
            Product name string
        """
        if not self.soup:
            raise ValueError("Page not fetched. Call fetch_page() first.")
        
        # Try multiple selectors for product name
        selectors = [
            'h1.item-name',
            'h1.itemName',
            'h1.product-title',
            'div.title h1',
            'h1',
            'div.product-name',
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
        return "unknown_sega_product"
    
    def get_image_urls(self) -> List[str]:
        """
        Extract all product image URLs from Sega page.
        
        Returns:
            List of full image URLs
        """
        if not self.soup:
            raise ValueError("Page not fetched. Call fetch_page() first.")
        
        image_urls = []
        
        # Strategy 1: Find images in product display area
        gallery_selectors = [
            'div.item-image img',
            'div.prize-image img',
            'div.product-img img',
            'div.image-gallery img',
            'ul.images img',
            'div.photo img',
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
        
        # Strategy 2: Look for image links (often high-res versions)
        if not image_urls:
            image_links = self.soup.find_all('a', href=True)
            for link in image_links:
                href = link.get('href')
                if href and any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    full_url = urljoin(self.url, href)
                    if full_url not in image_urls:
                        image_urls.append(full_url)
        
        # Strategy 3: Find all product images on page
        if not image_urls:
            all_images = self.soup.find_all('img')
            for img in all_images:
                src = img.get('src') or img.get('data-src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    # Filter out icons, logos, banners
                    if not any(word in src.lower() for word in ['icon', 'logo', 'banner', 'header', 'footer']):
                        full_url = urljoin(self.url, src)
                        if full_url not in image_urls:
                            image_urls.append(full_url)
        
        self.logger.info(f"Found {len(image_urls)} images for Sega product")
        return image_urls
