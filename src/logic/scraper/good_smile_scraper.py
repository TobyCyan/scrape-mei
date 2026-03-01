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
    
    VALID_DOMAINS = [
        'goodsmile.info',
        'goodsmileus.com',
        'goodsmilecompany.com',
    ]
    
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
        
        # Try multiple strategies in order of preference
        strategies = [
            self._extract_from_shopify_media_json,
            self._extract_from_schema_org_json,
            self._extract_from_open_graph_tags,
            self._extract_from_gallery_containers,
        ]
        
        for strategy in strategies:
            image_urls = strategy()
            if image_urls:
                self.logger.info(f"Found {len(image_urls)} images for Good Smile product")
                return image_urls
        
        self.logger.warning("No images found for Good Smile product")
        return []
    
    def _extract_from_shopify_media_json(self) -> List[str]:
        """Extract images from Shopify product media JSON in script tags."""
        image_urls = []
        script_pattern = re.compile(r'"media"\s*:\s*\[(.*?)\]', re.DOTALL)
        
        for script in self.soup.find_all('script'):
            if not script.string:
                continue
            
            match = script_pattern.search(script.string)
            if not match:
                continue
            
            try:
                media_json = '[' + match.group(1) + ']'
                media_data = json.loads(media_json)
                
                for item in media_data:
                    if not isinstance(item, dict):
                        continue
                    if item.get('media_type') != 'image' or 'src' not in item:
                        continue
                    
                    src = self._normalize_url(item['src'])
                    full_url = urljoin(self.url, src)
                    
                    if full_url not in image_urls:
                        image_urls.append(full_url)
                
                if image_urls:
                    break
            except (json.JSONDecodeError, KeyError):
                continue
        
        return image_urls
    
    def _extract_from_schema_org_json(self) -> List[str]:
        """Extract images from Schema.org Product JSON-LD."""
        image_urls = []
        
        for script in self.soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if not isinstance(data, dict) or 'image' not in data:
                    continue
                
                images = data['image']
                if isinstance(images, str):
                    images = [images]
                
                for img_url in images:
                    normalized_url = self._normalize_url(img_url)
                    full_url = urljoin(self.url, normalized_url)
                    
                    if full_url not in image_urls:
                        image_urls.append(full_url)
            except (json.JSONDecodeError, KeyError):
                continue
        
        return image_urls
    
    def _extract_from_open_graph_tags(self) -> List[str]:
        """Extract images from Open Graph meta tags."""
        image_urls = []
        
        for meta in self.soup.find_all('meta', property='og:image'):
            content = meta.get('content')
            if not content:
                continue
            
            normalized_url = self._normalize_url(content)
            full_url = urljoin(self.url, normalized_url)
            
            if full_url not in image_urls:
                image_urls.append(full_url)
        
        return image_urls
    
    def _extract_from_gallery_containers(self) -> List[str]:
        """Extract images from traditional product gallery containers."""
        image_urls = []
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
            if not images:
                continue
            
            for img in images:
                src = img.get('src') or img.get('data-src') or img.get('data-original')
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
    
    def _normalize_url(self, url: str) -> str:
        """Normalize a URL by adding protocol and removing query params."""
        if url.startswith('//'):
            url = 'https:' + url
        return url.split('?')[0]
    
    def _is_product_image(self, url: str) -> bool:
        """Check if a URL is likely a product image (not UI element or social media)."""
        excluded_patterns = [
            '_thumb.', '-thumb.', '/thumb.', 'thumb_', 'thumb-',
            'small', 'icon', 'logo', 'banner', 'btn', 'button', 'nav',
            'sns', 'twitter', 'facebook', 'instagram', 'social', 'share',
            'footer', 'header', 'sidebar'
        ]
        return not any(pattern in url.lower() for pattern in excluded_patterns)
