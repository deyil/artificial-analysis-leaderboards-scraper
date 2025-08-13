#!/usr/bin/env python3
"""
Main entry point for the Artificial Analysis Leaderboard Scraper.

This module orchestrates the scraping process by coordinating the scraper,
parser, and formatter components to extract and process leaderboard data
from the Artificial Analysis website.

Usage:
    python src/main.py
"""

import sys
import os

# Add the parent directory to sys.path so we can import from src.components
# This allows the script to be run directly with `python src/main.py`
# without requiring `python -m src.main` or installing the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from components.logger import setup_logger
from components.config import load_config
from components.scraper import fetch_html, fetch_html_with_playwright
from components.parser import parse_leaderboard
from components.formatter import write_to_csv


def main() -> None:
    """
    Main function that orchestrates the scraping process.
    
    This function coordinates all components to fetch, parse, and format
    the leaderboard data.
    """
    # Initialize the logger
    setup_logger()
    logger = logging.getLogger('web_scraper')
    
    # Load configuration
    config = load_config()
    
    # Log the start of the scraping process
    logger.info("Starting leaderboard scraping process")
    
    # Fetch HTML content from the target URL
    url = config.get('target_url')
    if not url:
        logger.error("Target URL not found in configuration")
        return
    
    html_content = fetch_html(url)
    if not html_content:
        logger.error("Failed to fetch HTML content from the target URL")
        return
    
    # Parse the leaderboard data from HTML
    leaderboard_data = parse_leaderboard(html_content)
    if not leaderboard_data:
        logger.info("No table found in initial HTML, attempting to render with Playwright")
        # Try fetching with Playwright
        html_content = fetch_html_with_playwright(url)
        if html_content:
            leaderboard_data = parse_leaderboard(html_content)
    
    if not leaderboard_data:
        logger.error("Failed to parse leaderboard data from HTML")
        return
    
    # Write the parsed data to CSV
    output_path = config.get('output_csv_path')
    if not output_path:
        logger.error("Output CSV path not found in configuration")
        return
    
    try:
        write_to_csv(leaderboard_data, output_path)
        logger.info("Leaderboard scraping process completed successfully")
    except Exception as e:
        logger.error(f"Failed to write data to CSV: {e}")


if __name__ == "__main__":
    main()
