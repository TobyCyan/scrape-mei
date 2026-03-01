# Quick Start Guide

## Installation & First Run

1. ** Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Test with a Product URL**
   - Open the GUI
   - Paste a product URL (e.g., from Good Smile Company)
   - Select the company from dropdown
   - Click "Start Scraping"
   - Watch the progress in real-time

## Example URLs for Testing

### Good Smile Company
```
https://www.goodsmile.info/en/product/[product-id]
```

### Kotobukiya
```
https://en.kotobukiya.co.jp/product/[product-id]
```

### Sega
```
https://segaprize.com/prize_item/[product-id]
```

## Creating an Executable

To create a standalone .exe file:

```bash
pyinstaller --onefile --windowed --name ScrapeMei main.py
```

The executable will be in the `dist/` folder.

## Troubleshooting Install Issues

### Issue: pip not found
Install Python 3.11+ from python.org and ensure "Add to PATH" is checked

### Issue: aiohttp won't install
```bash
pip install --upgrade pip
pip install aiohttp --no-cache-dir
```

### Issue: tkinter not available
Tkinter comes with Python. Reinstall Python with tcl/tk support.

## Next Steps

1. Test the application with a real product URL
2. Customize CSS selectors in scraper files if needed
3. Adjust download settings in main.py
4. Add more companies by following the README guide

## File Structure Overview

```
ScrapeMei/
├── main.py              # Start here - run this file
├── downloader.py        # Handles downloads
├── utils.py             # Helper functions
├── requirements.txt     # Install these packages
└── scraper/             # Scraper modules
    ├── base_scraper.py
    ├── good_smile_scraper.py
    ├── kotobukiya_scraper.py
    ├── sega_scraper.py
    └── scraper_factory.py
```

## Support

Check `logs/scraper.log` for detailed error messages if something goes wrong.
