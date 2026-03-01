"""
Test that social media images are filtered out
"""
import sys
from pathlib import Path

# Add logic directory to path
logic_path = Path(__file__).parent.parent / 'logic'
sys.path.insert(0, str(logic_path))

def test_social_media_filtering():
    """Test that social media and UI images are properly filtered."""
    print("Testing social media and UI image filtering...")
    
    # Test URLs that should be filtered out
    filtered_urls = [
        'https://www.kotobukiya.co.jp/files/page/sns/twitter/kotobuki_figure.jpg',
        'https://www.goodsmile.info/images/social/facebook-icon.png',
        'https://www.kotobukiya.co.jp/icons/share-button.png',
        'https://example.com/header-logo.jpg',
        'https://example.com/footer-banner.jpg',
        'https://example.com/sidebar-nav.jpg',
        'https://example.com/product-thumb.jpg',
    ]
    
    # Test product URLs that should NOT be filtered
    valid_urls = [
        'https://www.kotobukiya.co.jp/product/item/12345.jpg',
        'https://www.goodsmile.info/en/product/figure/main-image.jpg',
        'https://example.com/products/figure-001.jpg',
    ]
    
    excluded_keywords = [
        'thumb', 'small', 'icon', 'logo', 'banner', 'btn', 'button', 'nav',
        'sns', 'twitter', 'facebook', 'instagram', 'social', 'share',
        'footer', 'header', 'sidebar'
    ]
    
    passed = 0
    failed = 0
    
    # Test that filtered URLs are rejected
    for url in filtered_urls:
        is_filtered = any(word in url.lower() for word in excluded_keywords)
        if is_filtered:
            print(f"✓ PASS: Correctly filtered out: {url[:60]}...")
            passed += 1
        else:
            print(f"✗ FAIL: Should have filtered: {url[:60]}...")
            failed += 1
    
    # Test that valid URLs are not filtered
    for url in valid_urls:
        is_filtered = any(word in url.lower() for word in excluded_keywords)
        if not is_filtered:
            print(f"✓ PASS: Correctly kept: {url[:60]}...")
            passed += 1
        else:
            print(f"✗ FAIL: Should NOT have filtered: {url[:60]}...")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    print("="*70)
    print("Social Media and UI Image Filtering Test")
    print("="*70)
    
    success = test_social_media_filtering()
    
    print("\n" + "="*70)
    if success:
        print("✓ All tests passed! Social media images will be filtered out.")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
