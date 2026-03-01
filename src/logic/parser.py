"""
Scraper orchestration and coordination module.

This module contains the ScraperParser class which coordinates
the scraping and downloading process.
"""
from pathlib import Path
from typing import List
import logging

from scraper import ScraperFactory
from downloader import ImageDownloader
from utils import setup_logging, validate_url


class ScraperParser:
    """
    Main orchestrator class that coordinates scraping and downloading.
    
    Responsibilities:
    - Validate user inputs
    - Request scraper from factory
    - Coordinate scraping and downloading
    - Report status updates
    """
    
    def __init__(self, output_dir: str = 'downloads'):
        """
        Initialize the scraper parser.
        
        Args:
            output_dir: Base directory for downloaded images
        """
        self.output_dir = output_dir
        self.logger = setup_logging()
        self.downloader = ImageDownloader(output_dir=output_dir)
    
    def validate_inputs(self, url: str, company_type: str) -> tuple[bool, str]:
        """
        Validate user inputs.
        
        Args:
            url: Product page URL
            company_type: Company name
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not url or not url.strip():
            return False, "URL is required"
        
        if not validate_url(url):
            return False, "Invalid URL format"
        
        if not company_type or not company_type.strip():
            return False, "Company selection is required"
        
        return True, ""
    
    def scrape_product(
        self,
        url: str,
        company_type: str,
        progress_callback=None,
        completion_callback=None
    ):
        """
        Main scraping method - orchestrates the entire process.
        
        Args:
            url: Product page URL
            company_type: Company name
            progress_callback: Function to call with status updates
            completion_callback: Function to call when complete
        """
        try:
            # Validate inputs
            if not self._handle_validation(url, company_type, progress_callback, completion_callback):
                return
            
            # Create scraper
            scraper = self._create_scraper(url, company_type, progress_callback, completion_callback)
            if not scraper:
                return
            
            # Scrape product info
            product_name, image_urls = self._scrape_product_info(scraper, progress_callback, completion_callback)
            if not product_name:
                return
            
            # Check for images
            if not self._validate_images(image_urls, completion_callback):
                return
            
            # Download images
            self._download_images(url, product_name, image_urls, progress_callback, completion_callback)
            
        except Exception as e:
            self._handle_unexpected_error(e, completion_callback)
    
    def _handle_validation(self, url: str, company_type: str, progress_callback, completion_callback) -> bool:
        """Validate inputs and report errors."""
        if progress_callback:
            progress_callback("Validating inputs...")
        
        is_valid, error_msg = self.validate_inputs(url, company_type)
        if not is_valid:
            if completion_callback:
                completion_callback(False, error_msg)
            return False
        
        return True
    
    def _create_scraper(self, url: str, company_type: str, progress_callback, completion_callback):
        """Create scraper instance from factory."""
        if progress_callback:
            progress_callback(f"Creating scraper for {company_type}...")
        
        try:
            return ScraperFactory.get_scraper(company_type, url)
        except ValueError as e:
            if completion_callback:
                completion_callback(False, str(e))
            return None
    
    def _scrape_product_info(self, scraper, progress_callback, completion_callback) -> tuple:
        """Scrape product information from page."""
        if progress_callback:
            progress_callback("Fetching product page...")
        
        try:
            return scraper.scrape()
        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            self.logger.error(error_msg)
            if completion_callback:
                completion_callback(False, error_msg)
            return None, None
    
    def _validate_images(self, image_urls: List[str], completion_callback) -> bool:
        """Check if images were found."""
        if not image_urls:
            error_msg = "No images found on product page"
            self.logger.warning(error_msg)
            if completion_callback:
                completion_callback(False, error_msg)
            return False
        
        return True
    
    def _download_images(self, url: str, product_name: str, image_urls: List[str], 
                         progress_callback, completion_callback):
        """Download all product images."""
        if progress_callback:
            progress_callback(f"Found {len(image_urls)} images for '{product_name}'")
            progress_callback("Starting download...")
        
        def download_progress(current, total, message):
            if progress_callback:
                progress_callback(f"[{current}/{total}] {message}")
        
        successful, failed, download_path = self.downloader.download_images_sync(
            image_urls,
            product_name,
            download_progress,
            referer_url=url
        )
        
        result_msg = self._format_download_result(product_name, successful, failed, download_path)
        
        if completion_callback:
            completion_callback(True, result_msg)
    
    def _format_download_result(self, product_name: str, successful: int, 
                                 failed: int, download_path: Path) -> str:
        """Format the download completion message."""
        return (
            f"Download complete!\n\n"
            f"Product: {product_name}\n"
            f"Successfully downloaded: {successful}\n"
            f"Failed: {failed}\n"
            f"Location: {download_path.absolute()}"
        )
    
    def _handle_unexpected_error(self, error: Exception, completion_callback):
        """Handle unexpected errors during scraping."""
        error_msg = f"Unexpected error: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        if completion_callback:
            completion_callback(False, error_msg)
