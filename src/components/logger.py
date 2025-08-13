"""
Logging system for the Artificial Analysis Leaderboard Scraper.

This module configures and manages application logging with structured
logging and multiple output targets.

Key Features:
- Structured logging with multiple levels
- File and console output
- Request/response logging
- Error tracking and reporting
- Performance metrics logging
"""

import logging
import os
from typing import Optional


def setup_logger() -> logging.Logger:
    """
    Configure and return a logger named 'web_scraper'.
    
    The logger outputs to both console (DEBUG level) and file (INFO level)
    with the format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('web_scraper')
    logger.setLevel(logging.DEBUG)
    
    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create console handler with DEBUG level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Create file handler with INFO level
    file_handler = logging.FileHandler('logs/scraper.log')
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Set formatter to handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger