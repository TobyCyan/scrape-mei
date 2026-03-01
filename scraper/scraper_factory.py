"""
Factory class for creating company-specific scrapers.
"""
from typing import Dict, Type
import logging
from .base_scraper import BaseScraper
from .good_smile_scraper import GoodSmileScraper
from .kotobukiya_scraper import KotobukiyaScraper
from .sega_scraper import SegaScraper


class ScraperFactory:
    """
    Factory class that creates appropriate scraper instances based on company type.
    
    This implements the Factory Pattern for easy extensibility.
    To add a new company:
    1. Create a new scraper class inheriting from BaseScraper
    2. Register it in the _scrapers dictionary
    """
    
    # Registry of available scrapers
    _scrapers: Dict[str, Type[BaseScraper]] = {
        'good_smile': GoodSmileScraper,
        'kotobukiya': KotobukiyaScraper,
        'sega': SegaScraper,
    }
    
    # Mapping of alternative names to canonical names
    _aliases = {
        'goodsmile': 'good_smile',
        'good smile': 'good_smile',
        'good smile company': 'good_smile',
    }
    
    @classmethod
    def get_scraper(cls, company_type: str, url: str) -> BaseScraper:
        """
        Create and return a scraper instance for the specified company.
        
        Args:
            company_type: The company name (case-insensitive)
            url: The product page URL
            
        Returns:
            An instance of the appropriate scraper class
            
        Raises:
            ValueError: If the company type is not supported
        """
        logger = logging.getLogger('scraper')
        
        # Normalize company type (lowercase, no spaces)
        company_key = company_type.lower().strip().replace(' ', '_')
        
        # Check aliases first
        if company_key in cls._aliases:
            company_key = cls._aliases[company_key]
        
        scraper_class = cls._scrapers.get(company_key)
        
        if scraper_class is None:
            available = ', '.join(cls.get_supported_companies())
            error_msg = f"Unsupported company: '{company_type}'. Available: {available}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Creating scraper for company: {company_type}")
        return scraper_class(url)
    
    @classmethod
    def get_supported_companies(cls) -> list:
        """
        Get a list of supported company names.
        
        Returns:
            List of supported company names (deduplicated and sorted)
        """
        # Return unique, formatted company names from the main registry only
        companies = []
        for key in cls._scrapers.keys():
            # Convert to display format
            display_name = key.replace('_', ' ').title()
            companies.append(display_name)
        return sorted(companies)
    
    @classmethod
    def register_scraper(cls, company_type: str, scraper_class: Type[BaseScraper]) -> None:
        """
        Register a new scraper class (for extensibility).
        
        Args:
            company_type: The company name/identifier
            scraper_class: The scraper class to register
        """
        logger = logging.getLogger('scraper')
        company_key = company_type.lower().strip().replace(' ', '_')
        cls._scrapers[company_key] = scraper_class
        logger.info(f"Registered scraper for company: {company_type}")
