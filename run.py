"""
Launcher script for Anime Figurine Image Scraper.

This script adds the logic directory to the Python path and launches the main application.
"""
import sys
from pathlib import Path

# Add logic directory to path
logic_path = Path(__file__).parent / 'src' / 'logic'
sys.path.insert(0, str(logic_path))

# Import and run main
from main import main

if __name__ == "__main__":
    main()
