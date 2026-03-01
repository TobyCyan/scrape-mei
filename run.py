"""
Launcher script for Anime Figurine Image Scraper.

This script adds the logic directory to the Python path and launches the main application.
"""
import sys
import os
from pathlib import Path

# Determine if running as bundled executable or development
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = Path(sys._MEIPASS)
    logic_path = application_path / 'logic'
else:
    # Running in development
    application_path = Path(__file__).parent
    logic_path = application_path / 'src' / 'logic'

# Add logic directory to path
sys.path.insert(0, str(logic_path))

# Import and run main
from main import main

if __name__ == "__main__":
    main()
