"""
Main entry point for Anime Figurine Image Scraper.

This module serves as the application launcher and imports
the GUI and parser modules.
"""
import tkinter as tk

from gui import AnimeScraperGUI


def main():
    """Main entry point for the application."""
    # Fix DPI awareness for Windows to prevent blurry GUI
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    root = tk.Tk()
    app = AnimeScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
