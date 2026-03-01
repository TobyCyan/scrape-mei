"""
GUI module for Anime Figurine Image Scraper.

This module contains the GUI class which provides
a Tkinter-based graphical user interface.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading

from scraper import ScraperFactory
from parser import ScraperParser


class GUI:
    """
    Tkinter-based GUI for the Scrape Mei application.
    """
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Scrape Mei")
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
            text="Scrape Mei - Anime Figurine Image Scraper",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL input
        ttk.Label(main_frame, text="Product URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.clear_url_btn = ttk.Button(main_frame, text="Clear", command=self.clear_url)
        self.clear_url_btn.grid(row=1, column=2, padx=(5, 0), pady=5)
        
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
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', maximum=100)
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
    
    def clear_url(self):
        """Clear the URL field."""
        self.url_entry.delete(0, tk.END)
        self.url_entry.focus()
    
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
        
        # Reset and start progress bar
        self.progress.configure(mode='indeterminate')
        self.progress['value'] = 0
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
        
        # Complete the progress bar
        self.progress.stop()
        self.progress.configure(mode='determinate')
        self.progress['value'] = 100
        
        self.append_status("\n" + "="*50)
        self.append_status(message)
        self.append_status("="*50)
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
