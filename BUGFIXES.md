# Bug Fixes Applied

## Issue 1: Blurry GUI ✓ FIXED
**Problem**: GUI appeared blurry on high-DPI Windows displays.

**Solution**: Added Windows DPI awareness in `main.py`:
```python
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)
```

The GUI will now render sharply on high-resolution displays.

---

## Issue 2: Duplicate "Good Smile" Options ✓ FIXED
**Problem**: Dropdown showed "Good Smile" twice because the factory had both `'goodsmile'` and `'good_smile'` keys.

**Solution**: 
- Changed `scraper_factory.py` to use a single canonical name `'good_smile'` in the main registry
- Added an `_aliases` dictionary to map alternative names like `'goodsmile'` to the canonical name
- Modified `get_supported_companies()` to only return names from the main registry (no duplicates)

**Result**: Dropdown now shows each company exactly once, but you can still use any alias when calling the factory programmatically.

---

## Issue 3: Images Not Showing at File Path ✓ FIXED
**Problem**: Images weren't being saved due to event loop error (see Issue 4).

**Solution**: Fixed by resolving the event loop issue. Images now download correctly to:
```
downloads/<sanitized_product_name>/
  ├─ <product>_001.jpg
  ├─ <product>_002.jpg
  └─ ...
```

---

## Issue 4: asyncio.locks.Semaphore Event Loop Error ✓ FIXED
**Problem**: Error message:
```
Exception: <asyncio.locks.Semaphore object> is bound to a different event loop
```

**Root Cause**: The semaphore was created in `__init__()` when the ImageDownloader was instantiated in the main thread, but then used in a different event loop created by the worker thread.

**Solution**: 
1. Removed semaphore creation from `__init__()`
2. Create the semaphore inside the `download_all()` async method (in the correct event loop)
3. Pass the semaphore as a parameter to `download_image()`

**Code changes in `downloader.py`**:
```python
# In download_all():
semaphore = asyncio.Semaphore(self.max_concurrent)

# In download_image():
async def download_image(self, session, url, filepath, semaphore, ...):
    async with semaphore:
        # ... download logic
```

This ensures the semaphore is always created and used in the same event loop.

---

## Testing

Run the verification test:
```bash
python src/tests/test_fixes.py
```

Expected output:
```
✓ All 3 tests passed!

Fixed issues:
  1. ✓ DPI awareness added (GUI should be sharper)
  2. ✓ Good Smile only appears once in dropdown
  3. ✓ Event loop issue fixed (images will download)
  4. ✓ Company aliases work correctly
```

---

## Ready to Use

The application is now fully functional. Try it out:
```bash
python run.py
```

All issues have been resolved!
