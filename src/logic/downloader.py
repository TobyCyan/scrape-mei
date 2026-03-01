"""
Image downloader with async support for parallel downloads.
"""
import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import List, Tuple, Callable
from utils import sanitize_filename, ensure_directory


class ImageDownloader:
    """
    Handles asynchronous downloading of images with retry logic.
    """
    
    def __init__(self, output_dir: str = 'downloads', max_concurrent: int = 5, max_retries: int = 3):
        """
        Initialize the image downloader.
        
        Args:
            output_dir: Base directory for downloads
            max_concurrent: Maximum number of concurrent downloads
            max_retries: Maximum number of retry attempts per image
        """
        self.output_dir = Path(output_dir)
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.logger = logging.getLogger('scraper')
        
    async def download_image(
        self,
        session: aiohttp.ClientSession,
        url: str,
        filepath: Path,
        semaphore: asyncio.Semaphore,
        retry_count: int = 0
    ) -> Tuple[bool, str]:
        """
        Download a single image with retry logic.
        
        Args:
            session: aiohttp session
            url: Image URL
            filepath: Destination file path
            semaphore: Semaphore for concurrency control
            retry_count: Current retry attempt
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        async with semaphore:
            try:
                self.logger.info(f"Downloading: {url}")
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Ensure parent directory exists
                        filepath.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Write file
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        
                        self.logger.info(f"Saved: {filepath.name}")
                        return True, f"Downloaded: {filepath.name}"
                    else:
                        error_msg = f"HTTP {response.status} for {url}"
                        self.logger.warning(error_msg)
                        
                        # Retry on server errors
                        if response.status >= 500 and retry_count < self.max_retries:
                            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                            return await self.download_image(session, url, filepath, semaphore, retry_count + 1)
                        
                        return False, error_msg
                        
            except asyncio.TimeoutError:
                error_msg = f"Timeout downloading {url}"
                self.logger.warning(error_msg)
                
                if retry_count < self.max_retries:
                    await asyncio.sleep(2 ** retry_count)
                    return await self.download_image(session, url, filepath, semaphore, retry_count + 1)
                
                return False, error_msg
                
            except Exception as e:
                error_msg = f"Error downloading {url}: {str(e)}"
                self.logger.error(error_msg)
                
                if retry_count < self.max_retries:
                    await asyncio.sleep(2 ** retry_count)
                    return await self.download_image(session, url, filepath, semaphore, retry_count + 1)
                
                return False, error_msg
    
    async def download_all(
        self,
        image_urls: List[str],
        product_name: str,
        progress_callback: Callable[[int, int, str], None] = None,
        referer_url: str = None
    ) -> Tuple[int, int, Path]:
        """
        Download all images asynchronously.
        
        Args:
            image_urls: List of image URLs to download
            product_name: Product name for folder creation
            progress_callback: Optional callback function(current, total, message)
            referer_url: Optional product page URL for Referer header
            
        Returns:
            Tuple of (successful_count, failed_count, download_path)
        """
        # Deduplicate URLs
        unique_urls = list(dict.fromkeys(image_urls))
        total = len(unique_urls)
        
        if total == 0:
            self.logger.warning("No images to download")
            return 0, 0, self.output_dir
        
        # Create product directory
        sanitized_name = sanitize_filename(product_name)
        product_dir = self.output_dir / sanitized_name
        ensure_directory(product_dir)
        
        self.logger.info(f"Downloading {total} images to: {product_dir}")
        
        # Download all images
        successful = 0
        failed = 0
        
        # Create semaphore in the same event loop
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Set up headers with Referer if provided (required by some sites like Kotobukiya)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
        }
        if referer_url:
            headers['Referer'] = referer_url
        
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            
            for idx, url in enumerate(unique_urls, 1):
                # Determine file extension
                ext = Path(url).suffix
                if not ext or len(ext) > 5:
                    ext = '.jpg'
                
                # Create filename
                filename = f"{sanitized_name}_{idx:03d}{ext}"
                filepath = product_dir / filename
                
                # Create download task
                task = self.download_image(session, url, filepath, semaphore)
                tasks.append(task)
            
            # Execute downloads and gather results
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for idx, result in enumerate(results, 1):
                if isinstance(result, Exception):
                    failed += 1
                    message = f"Exception: {str(result)}"
                    self.logger.error(message)
                elif result[0]:  # Success
                    successful += 1
                    message = result[1]
                else:  # Failed
                    failed += 1
                    message = result[1]
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(idx, total, message)
        
        self.logger.info(f"Download complete: {successful} successful, {failed} failed")
        return successful, failed, product_dir
    
    def download_images_sync(
        self,
        image_urls: List[str],
        product_name: str,
        progress_callback: Callable[[int, int, str], None] = None,
        referer_url: str = None
    ) -> Tuple[int, int, Path]:
        """
        Synchronous wrapper for async download_all method.
        
        Args:
            image_urls: List of image URLs to download
            product_name: Product name for folder creation
            progress_callback: Optional callback function(current, total, message)
            referer_url: Optional product page URL for Referer header
            
        Returns:
            Tuple of (successful_count, failed_count, download_path)
        """
        # Create new event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self.download_all(image_urls, product_name, progress_callback, referer_url)
            )
            return result
        finally:
            loop.close()
