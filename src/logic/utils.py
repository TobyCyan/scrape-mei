"""
Utility functions for the anime figurine scraper.
"""
import re
import logging
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """
    Sanitize a product name for use as a filename or directory name.
    
    Args:
        name: The product name to sanitize
        
    Returns:
        Sanitized name (lowercase, alphanumeric + underscores)
    """
    # Remove or replace special characters
    name = re.sub(r'[^\w\s-]', '', name)
    # Replace whitespace with underscores
    name = re.sub(r'[\s-]+', '_', name)
    # Convert to lowercase
    name = name.lower().strip('_')
    # Limit length to avoid filesystem issues
    return name[:100] if name else 'unknown_product'


def setup_logging(log_dir: str = 'logs') -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_dir: Directory to store log files
        
    Returns:
        Configured logger instance
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    log_file = log_path / 'scraper.log'
    
    # Create logger
    logger = logging.getLogger('scraper')
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def validate_url(url: str) -> bool:
    """
    Basic URL validation.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL appears valid, False otherwise
    """
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def ensure_directory(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)
