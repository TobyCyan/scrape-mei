"""
Main GUI application for Anime Figurine Image Scraper.

This module contains:
- ScraperParser: Orchestrates the scraping process
- AnimeScraperGUI: Tkinter-based user interface
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from typing import Optional
import logging

from scraper import ScraperFactory
from downloader import ImageDownloader
from utils import setup_logging, validate_url


class ScraperParser:
    """
    Main orchestrator class that coordinates scraping and downloading.
    
    Responsibilities:
    - Validate user inputs
    - Request scraper from factory
    - Coordinate scraping and downloading
    - Report status updates
    """
    
    def __init__(self, output_dir: str = 'downloads'):
        """
        Initialize the scraper parser.
        
        Args:
            output_dir: Base directory for downloaded images
        """
        self.output_dir = output_dir
        self.logger = setup_logging()
        self.downloader = ImageDownloader(output_dir=output_dir)
    
    def validate_inputs(self, url: str, company_type: str) -> tuple[bool, str]:
        """
        Validate user inputs.
        
        Args:
            url: Product page URL
            company_type: Company name
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not url or not url.strip():
            return False, "URL is required"
        
        if not validate_url(url):
            return False, "Invalid URL format"
        
        if not company_type or not company_type.strip():
            return False, "Company selection is required"
        
        return True, ""
    
    def scrape_product(
        self,
        url: str,
        company_type: str,
        progress_callback=None,
        completion_callback=None
    ):
        """
        Main scraping method - orchestrates the entire process.
        
        Args:
            url: Product page URL
            company_type: Company name
            progress_callback: Function to call with status updates
            completion_callback: Function to call when complete
        """
        try:
            # Update status
            if progress_callback:
                progress_callback("Validating inputs...")
            
            # Validate inputs
            is_valid, error_msg = self.validate_inputs(url, company_type)
            if not is_valid:
                if completion_callback:
                    completion_callback(False, error_msg)
                return
            
            # Update status
            if progress_callback:
                progress_callback(f"Creating scraper for {company_type}...")
            
            # Get scraper from factory
            try:
                scraper = ScraperFactory.get_scraper(company_type, url)
            except ValueError as e:
                if completion_callback:
                    completion_callback(False, str(e))
                return
            
            # Update status
            if progress_callback:
                progress_callback("Fetching product page...")
            
            # Scrape product information
            try:
                product_name, image_urls = scraper.scrape()
            except Exception as e:
                error_msg = f"Scraping failed: {str(e)}"
                self.logger.error(error_msg)
                if completion_callback:
                    completion_callback(False, error_msg)
                return
            
            # Check if images were found
            if not image_urls:
                error_msg = "No images found on product page"
                self.logger.warning(error_msg)
                if completion_callback:
                    completion_callback(False, error_msg)
                return
            
            # Update status
            if progress_callback:
                progress_callback(f"Found {len(image_urls)} images for '{product_name}'")
                progress_callback("Starting download...")
            
            # Download images
            def download_progress(current, total, message):
                if progress_callback:
                    progress_callback(f"[{current}/{total}] {message}")
            
            successful, failed, download_path = self.downloader.download_images_sync(
                image_urls,
                product_name,
                download_progress
            )
            
            # Report completion
            result_msg = (
                f"Download complete!\n\n"
                f"Product: {product_name}\n"
                f"Successfully downloaded: {successful}\n"
                f"Failed: {failed}\n"
                f"Location: {download_path.absolute()}"
            )
            
            if completion_callback:
                completion_callback(True, result_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            if completion_callback:
                completion_callback(False, error_msg)


class AnimeScraperGUI:
    """
    Tkinter-based GUI for the anime figurine scraper.
    """
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Anime Figurine Image Scraper")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        self.parser = ScraperParser()
        self.is_scraping = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Anime Figurine Image Scraper",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL input
        ttk.Label(main_frame, text="Product URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Company selection
        ttk.Label(main_frame, text="Company:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.company_var = tk.StringVar()
        
        # Get supported companies
        companies = ScraperFactory.get_supported_companies()
        self.company_combo = ttk.Combobox(
            main_frame,
            textvariable=self.company_var,
            values=companies,
            state='readonly',
            width=30
        )
        if companies:
            self.company_combo.current(0)
        self.company_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(main_frame, width=40)
        self.output_entry.insert(0, "downloads")
        self.output_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_directory)
        self.browse_btn.grid(row=3, column=2, padx=(5, 0), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=15)
        
        self.scrape_btn = ttk.Button(
            button_frame,
            text="Start Scraping",
            command=self.start_scraping,
            width=20
        )
        self.scrape_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form,
            width=15
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Status display
        ttk.Label(main_frame, text="Status:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)
        
        self.status_text = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            width=60,
            wrap=tk.WORD,
            state='disabled'
        )
        self.status_text.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def browse_directory(self):
        """Open directory browser dialog."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)
    
    def clear_form(self):
        """Clear all form inputs and status."""
        if self.is_scraping:
            messagebox.showwarning("Warning", "Cannot clear while scraping is in progress")
            return
        
        self.url_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, "downloads")
        self.status_text.configure(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.configure(state='disabled')
    
    def append_status(self, message: str):
        """
        Append a message to the status display.
        
        Args:
            message: Status message to display
        """
        self.status_text.configure(state='normal')
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state='disabled')
    
    def start_scraping(self):
        """Start the scraping process in a separate thread."""
        if self.is_scraping:
            messagebox.showwarning("Warning", "Scraping already in progress")
            return
        
        # Get inputs
        url = self.url_entry.get().strip()
        company = self.company_var.get()
        output_dir = self.output_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a product URL")
            return
        
        if not company:
            messagebox.showerror("Error", "Please select a company")
            return
        
        # Update parser output directory
        self.parser.output_dir = output_dir
        self.parser.downloader.output_dir = Path(output_dir)
        
        # Clear status
        self.status_text.configure(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.configure(state='disabled')
        
        # Update UI state
        self.is_scraping = True
        self.scrape_btn.configure(state='disabled')
        self.clear_btn.configure(state='disabled')
        self.progress.start()
        
        # Progress callback
        def progress_callback(message):
            self.root.after(0, lambda: self.append_status(message))
        
        # Completion callback
        def completion_callback(success, message):
            self.root.after(0, lambda: self.on_scraping_complete(success, message))
        
        # Start scraping in separate thread
        thread = threading.Thread(
            target=self.parser.scrape_product,
            args=(url, company, progress_callback, completion_callback),
            daemon=True
        )
        thread.start()
    
    def on_scraping_complete(self, success: bool, message: str):
        """
        Handle scraping completion.
        
        Args:
            success: Whether scraping was successful
            message: Result or error message
        """
        self.is_scraping = False
        self.scrape_btn.configure(state='normal')
        self.clear_btn.configure(state='normal')
        self.progress.stop()
        
        self.append_status("\n" + "="*50)
        self.append_status(message)
        self.append_status("="*50)
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)


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
