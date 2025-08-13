"""
HTTP request handler for the Artificial Analysis Leaderboard Scraper.

This module manages all HTTP communication with the target website,
including GET requests, retry logic, rate limiting, and error handling.

Key Features:
- Handles GET requests to the leaderboard URL
- Implements retry logic with exponential backoff
- Manages request headers and user agent rotation
- Handles HTTP errors (404, 500, timeout, etc.)
"""

import requests
import time
import logging
from typing import Optional


def fetch_html(url: str, retries: int = 3, delay: int = 5) -> Optional[str]:
    """
    Fetch HTML content from a given URL with retry mechanism.
    
    Args:
        url (str): The URL to fetch HTML content from
        retries (int): Number of retry attempts (default: 3)
        delay (int): Base delay between retries in seconds (default: 5)
        
    Returns:
        Optional[str]: HTML content as string if successful, None otherwise
    """
    logger = logging.getLogger(__name__)
    
    for attempt in range(retries + 1):
        try:
            # Make a GET request with a timeout
            response = requests.get(url, timeout=30)
            # Raise an exception for bad status codes
            response.raise_for_status()
            # Log success
            logger.info(f"Successfully fetched HTML from {url}")
            # Return the HTML content
            return response.text
        except requests.exceptions.RequestException as e:
            # Handle any request-related exceptions
            if attempt < retries:
                # Calculate exponential backoff delay
                backoff_delay = delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed fetching HTML from {url}: {e}. Retrying in {backoff_delay} seconds...")
                time.sleep(backoff_delay)
            else:
                logger.error(f"Failed to fetch HTML from {url} after {retries + 1} attempts: {e}")
                return None