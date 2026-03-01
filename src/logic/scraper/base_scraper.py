"""
Base scraper abstract class for all company-specific scrapers.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import logging


class BaseScraper(ABC):
    """
    Abstract base class for company-specific scrapers.
    
    All company scrapers must implement:
    - get_product_name()
    - get_image_urls()
    - VALID_DOMAINS (class attribute)
    """
    
    # Each scraper must define valid domains
    VALID_DOMAINS: List[str] = []
    
    def __init__(self, url: str):
        """
        Initialize the scraper with a product URL.
        
        Args:
            url: The product page URL
            
        Raises:
            ValueError: If URL domain doesn't match company's valid domains
        """
        self.url = url
        self.soup = None
        self.logger = logging.getLogger('scraper')
        
        # Validate URL domain matches company
        if not self.validate_url():
            valid_domains = ', '.join(self.VALID_DOMAINS)
            raise ValueError(
                f"URL domain mismatch: '{url}' does not match expected domains for {self.__class__.__name__}. "
                f"Valid domains: {valid_domains}"
            )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',  # Removed 'br' to avoid Brotli compression issues
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def fetch_page(self) -> BeautifulSoup:
        """
        Fetch the product page and parse with BeautifulSoup.
        
        Returns:
            BeautifulSoup object of the page
            
        Raises:
            requests.RequestException: If the page cannot be fetched
        """
        try:
            self.logger.info(f"Fetching page: {self.url}")
            
            # Create a session to handle cookies and maintain connection
            session = requests.Session()
            session.headers.update(self.headers)
            
            # Add slight delay to avoid rate limiting
            import time
            time.sleep(1)
            
            response = session.get(self.url, timeout=30)
            response.raise_for_status()
            # Use response.text instead of response.content to handle decompression and encoding
            self.soup = BeautifulSoup(response.text, 'html.parser')
            return self.soup
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch page: {e}")
            raise
    
    def validate_url(self) -> bool:
        """
        Validate that the URL domain matches the company's expected domains.
        
        Returns:
            True if URL is valid for this scraper, False otherwise
        """
        if not self.VALID_DOMAINS:
            self.logger.warning(f"{self.__class__.__name__} has no VALID_DOMAINS defined")
            return True  # Allow if not configured
        
        try:
            parsed = urlparse(self.url)
            domain = parsed.netloc.lower()
            
            # Check if domain matches any valid domain
            for valid_domain in self.VALID_DOMAINS:
                if valid_domain.lower() in domain:
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error validating URL: {e}")
            return False
    
    @abstractmethod
    def get_product_name(self) -> str:
        """
        Extract the product name from the page.
        
        Returns:
            Product name as a string
        """
        pass
    
    @abstractmethod
    def get_image_urls(self) -> List[str]:
        """
        Extract all product image URLs from the page.
        
        Returns:
            List of image URLs
        """
        pass
    
    def scrape(self) -> Tuple[str, List[str]]:
        """
        Main scraping method - fetches page and extracts product info.
        
        Returns:
            Tuple of (product_name, image_urls)
        """
        self.fetch_page()
        product_name = self.get_product_name()
        image_urls = self.get_image_urls()
        
        self.logger.info(f"Scraped product: {product_name}")
        self.logger.info(f"Found {len(image_urls)} images")
        
        return product_name, image_urls
