import logging
from logging.handlers import TimedRotatingFileHandler
import os

def setup_logging():
    """
    Sets up a timed rotating file logger for the application.
    """
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'photo_sorter.log')

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a timed rotating file handler
    # Rotates every day (at midnight), keeps 7 days of backups
    handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
    handler.setLevel(logging.INFO)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    # Avoid adding handlers if they already exist
    if not logger.handlers:
        logger.addHandler(handler)

    # Also log to console for immediate feedback during development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(console_handler)

    logging.info("Logging setup complete.")

