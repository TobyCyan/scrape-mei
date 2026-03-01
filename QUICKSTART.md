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

### Standard Build (Single .exe file)
```bash
python build.py
```
or simply double-click `build.bat`

Creates a single `ScrapeMei.exe` file (~18 MB) in `dist/` folder.

### Folder Distribution (Recommended if you get errors)
```bash
python build_folder.py
```

Creates `dist/ScrapeMei/` folder with .exe and dependencies.  
**More reliable** - avoids single-file extraction issues.

### Debug Build (For troubleshooting)
```bash
python build.py --debug
```

Creates .exe with visible console window to see error messages.

**How it works:**
- Reads all dependencies from `requirements.txt`
- Automatically bundles everything
- No Python installation required on target machines!

### Manual Build (Advanced)
```bash
pyinstaller --onefile --windowed --name ScrapeMei --noupx run.py
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

### Issue: "Failed to start python embedded interpreter"
This error occurs when running the .exe. Try these fixes:

**Quick Fixes:**
1. Use folder distribution: `python build_folder.py`
2. Run in debug mode: `python build.py --debug` (shows error details)
3. Disable antivirus temporarily or add `dist/` folder to exclusions
4. Install [Visual C++ Redistributables](https://aka.ms/vs/17/release/vc_redist.x64.exe)
5. Run .exe as administrator (right-click → "Run as administrator")

**Most Reliable:** Use the folder distribution (`build_folder.py`), which distributes the entire folder as a .zip file.

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
├── build.py             # Standard build script (single .exe)
├── build_folder.py      # Folder distribution build (more reliable)
├── build.bat            # Windows build wrapper
├── requirements.txt     # Python dependencies (auto-parsed by build.py)
├── README.md            # Full documentation
├── QUICKSTART.md        # Quick setup guide
└── src/logic/           # Source code
    ├── main.py          # Application launcher
    ├── gui.py           # GUI components
    ├── parser.py        # Scraping orchestrator
    ├── downloader.py    # Async image downloads
    ├── utils.py         # Helper functions
   └── scraper/         # Scraper modules (base/factory/company scrapers)
      └── ...
```

## Support

Check `logs/scraper.log` for detailed error messages if something goes wrong.
