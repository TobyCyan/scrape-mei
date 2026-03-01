"""
Base scraper abstract class for all company-specific scrapers.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
import logging


class BaseScraper(ABC):
    """
    Abstract base class for company-specific scrapers.
    
    All company scrapers must implement:
    - get_product_name()
    - get_image_urls()
    """
    
    def __init__(self, url: str):
        """
        Initialize the scraper with a product URL.
        
        Args:
            url: The product page URL
        """
        self.url = url
        self.soup = None
        self.logger = logging.getLogger('scraper')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
            return self.soup
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch page: {e}")
            raise
    
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
