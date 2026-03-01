"""
Test script to verify installation and basic functionality.
"""
import sys
from pathlib import Path

# Add logic directory to path
logic_path = Path(__file__).parent.parent / 'logic'
sys.path.insert(0, str(logic_path))


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import requests
        print("✓ requests")
    except ImportError:
        print("✗ requests - Run: pip install requests")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4")
    except ImportError:
        print("✗ beautifulsoup4 - Run: pip install beautifulsoup4")
        return False
    
    try:
        import aiohttp
        print("✓ aiohttp")
    except ImportError:
        print("✗ aiohttp - Run: pip install aiohttp")
        return False
    
    try:
        import lxml
        print("✓ lxml")
    except ImportError:
        print("✗ lxml - Run: pip install lxml")
        return False
    
    try:
        import tkinter
        print("✓ tkinter")
    except ImportError:
        print("✗ tkinter - Reinstall Python with tcl/tk support")
        return False
    
    return True


def test_modules():
    """Test that all project modules can be imported."""
    print("\nTesting project modules...")
    
    try:
        from utils import sanitize_filename, setup_logging, validate_url
        print("✓ utils")
    except ImportError as e:
        print(f"✗ utils - {e}")
        return False
    
    try:
        from scraper import BaseScraper, ScraperFactory
        print("✓ scraper package")
    except ImportError as e:
        print(f"✗ scraper package - {e}")
        return False
    
    try:
        from scraper import GoodSmileScraper, KotobukiyaScraper, SegaScraper
        print("✓ company scrapers")
    except ImportError as e:
        print(f"✗ company scrapers - {e}")
        return False
    
    try:
        from downloader import ImageDownloader
        print("✓ downloader")
    except ImportError as e:
        print(f"✗ downloader - {e}")
        return False
    
    return True


def test_factory():
    """Test the scraper factory."""
    print("\nTesting scraper factory...")
    
    try:
        from scraper import ScraperFactory
        
        companies = ScraperFactory.get_supported_companies()
        print(f"✓ Supported companies: {', '.join(companies)}")
        
        # Test creating a scraper
        test_url = "https://www.example.com/product/123"
        scraper = ScraperFactory.get_scraper("goodsmile", test_url)
        print(f"✓ Created scraper: {scraper.__class__.__name__}")
        
        return True
    except Exception as e:
        print(f"✗ Factory test failed - {e}")
        return False


def test_utilities():
    """Test utility functions."""
    print("\nTesting utilities...")
    
    try:
        from utils import sanitize_filename, validate_url
        
        # Test sanitization
        test_name = "Test Product! (2024) [Special Edition]"
        sanitized = sanitize_filename(test_name)
        print(f"✓ Sanitize: '{test_name}' -> '{sanitized}'")
        
        # Test URL validation
        valid_url = "https://www.example.com/product"
        invalid_url = "not-a-url"
        
        assert validate_url(valid_url) == True
        assert validate_url(invalid_url) == False
        print(f"✓ URL validation working")
        
        return True
    except Exception as e:
        print(f"✗ Utility test failed - {e}")
        return False


def main():
    """Run all tests."""
    print("="*50)
    print("ScrapeMei - Installation Test")
    print("="*50)
    
    results = []
    
    # Test imports
    results.append(("Package imports", test_imports()))
    
    # Test modules
    results.append(("Project modules", test_modules()))
    
    # Test factory
    results.append(("Scraper factory", test_factory()))
    
    # Test utilities
    results.append(("Utility functions", test_utilities()))
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("\n✓ All tests passed! You're ready to run the application.")
        print("\nNext steps:")
        print("  1. Run: python main.py")
        print("  2. Enter a product URL")
        print("  3. Select a company")
        print("  4. Click 'Start Scraping'")
        return 0
    else:
        print("\n✗ Some tests failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
