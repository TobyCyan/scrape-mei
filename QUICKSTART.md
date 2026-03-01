# Quick Start Guide

## Installation & First Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python run.py
   ```

3. **Test with a Product URL**
   - Open the GUI
   - Paste a product URL (e.g., from Good Smile Company)
   - Select the company from dropdown
   - Choose an output directory (or use default: `downloads/`)
   - Click "Start Scraping"
   - Watch the progress bar and status updates in real-time

## Example URLs for Testing

### Good Smile Company
```
https://www.goodsmile.info/en/product/[product-id]
```

### Kotobukiya
```
https://en.kotobukiya.co.jp/product/[product-id]
```

## Creating an Executable

To create a standalone .exe file (Windows):

### Automated Build (Recommended)
```bash
python build.py
```
or simply double-click `build.bat`

The build script automatically:
- Reads all dependencies from `requirements.txt`
- Bundles everything into a single executable
- Places the .exe in the `dist/` folder

**No Python installation required on target machines!**

### Manual Build (Advanced)
```bash
pyinstaller --onefile --windowed --name ScrapeMei run.py
```

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

### Issue: Build fails with PyInstaller
```bash
pip install --upgrade pyinstaller
python build.py
```

### Issue: Executable missing dependencies
The build script automatically reads `requirements.txt`. If you added a new package:
1. Add it to `requirements.txt`
2. Run `python build.py` again
3. All dependencies are auto-detected and bundled

## Next Steps

1. Test the application with real product URLs
2. Run tests with `python run_tests.py`
3. Build executable with `python build.py` for distribution
4. Customize scraper logic in `src/logic/scraper/` if needed
5. Add new dependencies to `requirements.txt` (auto-included in next build)
6. Add more companies by extending `BaseScraper` class

## File Structure Overview

```
ScrapeMei/
├── run.py               # Entry point - run this file
├── build.py             # Automated build script
├── build.bat            # Windows build wrapper
├── requirements.txt     # Python dependencies (auto-parsed by build.py)
└── src/logic/           # Source code
    ├── main.py          # Application launcher
    ├── gui.py           # GUI components
    ├── parser.py        # Scraping orchestrator
    ├── downloader.py    # Async image downloads
    ├── utils.py         # Helper functions
    └── scraper/         # Scraper modules
        ├── base_scraper.py
        ├── good_smile_scraper.py
        ├── kotobukiya_scraper.py
        └── scraper_factory.py
```

## Support

Check `logs/scraper.log` for detailed error messages if something goes wrong.
