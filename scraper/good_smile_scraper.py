"""
Good Smile Company scraper implementation.
"""
from typing import List
from urllib.parse import urljoin
import json
import re
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
            'h1.product__title',  # Good Smile US (Shopify)
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
        
        # Try Open Graph meta tag
        og_title = self.soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            name = og_title.get('content').strip()
            self.logger.info(f"Found product name from OG tag: {name}")
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
        
        # Strategy 1: Look for Shopify product "media" JSON in script tags (most complete)
        script_pattern = re.compile(r'"media"\s*:\s*\[(.*?)\]', re.DOTALL)
        all_scripts = self.soup.find_all('script')
        for script in all_scripts:
            if script.string:
                match = script_pattern.search(script.string)
                if match:
                    try:
                        # Extract media array
                        media_json = '[' + match.group(1) + ']'
                        media_data = json.loads(media_json)
                        for item in media_data:
                            if isinstance(item, dict) and 'src' in item and item.get('media_type') == 'image':
                                src = item['src']
                                if src.startswith('//'):
                                    src = 'https:' + src
                                # Remove query params
                                src = src.split('?')[0]
                                full_url = urljoin(self.url, src)
                                if full_url not in image_urls:
                                    image_urls.append(full_url)
                        if image_urls:
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        # Strategy 2: Parse Shopify Schema.org JSON-LD (fallback)
        if not image_urls:
            script_tags = self.soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'image' in data:
                        # Schema.org Product JSON
                        images = data['image']
                        if isinstance(images, str):
                            images = [images]
                        for img_url in images:
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            full_url = urljoin(self.url, img_url)
                            # Remove query params for better quality
                            full_url = full_url.split('?')[0]
                            if full_url not in image_urls:
                                image_urls.append(full_url)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # Strategy 3: Check Open Graph meta tags
        if not image_urls:
            og_images = self.soup.find_all('meta', property='og:image')
            for meta in og_images:
                content = meta.get('content')
                if content:
                    if content.startswith('//'):
                        content = 'https:' + content
                    # Remove query params
                    content = content.split('?')[0]
                    full_url = urljoin(self.url, content)
                    if full_url not in image_urls:
                        image_urls.append(full_url)
        
        # Strategy 4: Find images in traditional product gallery containers (Good Smile Info)
        if not image_urls:
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
        
        self.logger.info(f"Found {len(image_urls)} images for Good Smile product")
        return image_urls
