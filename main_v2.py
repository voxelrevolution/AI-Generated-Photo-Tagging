# /Reserved/Photo Sorter V2/main.py

"""
Rapid Photo Sorter V2 - Main Entry Point

This script initializes and runs the V2 application.
The core application logic is now modular and resides within the 'app/' directory.
This file is responsible for:
- Importing the main application class.
- Creating the root Tkinter window.
- Instantiating and launching the application.
"""

import tkinter as tk
import logging
from app.app import PhotoSorterApp
from app.utils.logging_handler import setup_logging

def main():
    """
    Initializes the Tkinter root and runs the main application loop.
    """
    # Set up logging first
    setup_logging()
    logging.info("Application starting.")
    
    root = tk.Tk()
    app = PhotoSorterApp(root)
    
    # Add a handler for the window closing event
    def on_closing():
        logging.info("Application window closed by user.")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()
    logging.info("Application finished.")

if __name__ == "__main__":
    main()
