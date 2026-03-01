"""
Test URL validation for scrapers
"""
import sys
from pathlib import Path

# Add logic directory to path
logic_path = Path(__file__).parent.parent / 'logic'
sys.path.insert(0, str(logic_path))

def test_url_validation():
    """Test that scrapers validate URLs correctly."""
    print("Testing URL validation...")
    from scraper import ScraperFactory
    
    test_cases = [
        # (company, url, should_succeed)
        ('Good Smile', 'https://www.goodsmile.info/en/product/12345', True),
        ('Good Smile', 'https://www.goodsmileus.com/products/test', True),
        ('Good Smile', 'https://www.kotobukiya.co.jp/product/test', False),
        ('Kotobukiya', 'https://en.kotobukiya.co.jp/product/12345', True),
        ('Kotobukiya', 'https://www.kotobukiya.co.jp/product/test', True),
        ('Kotobukiya', 'https://www.goodsmile.info/en/product/test', False),
    ]
    
    passed = 0
    failed = 0
    
    for company, url, should_succeed in test_cases:
        try:
            scraper = ScraperFactory.get_scraper(company, url)
            if should_succeed:
                print(f"✓ PASS: {company} accepted {url[:50]}...")
                passed += 1
            else:
                print(f"✗ FAIL: {company} should have rejected {url[:50]}...")
                failed += 1
        except ValueError as e:
            if not should_succeed:
                print(f"✓ PASS: {company} correctly rejected {url[:50]}...")
                passed += 1
            else:
                print(f"✗ FAIL: {company} incorrectly rejected {url[:50]}...")
                print(f"   Error: {e}")
                failed += 1
        except Exception as e:
            print(f"✗ FAIL: Unexpected error for {company} with {url[:50]}...")
            print(f"   Error: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    print("="*60)
    print("URL Validation Test")
    print("="*60)
    
    success = test_url_validation()
    
    print("\n" + "="*60)
    if success:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
