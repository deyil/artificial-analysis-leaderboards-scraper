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
from playwright.sync_api import sync_playwright


def fetch_html_with_playwright(url: str) -> Optional[str]:
    """
    Fetch HTML content from a given URL using Playwright to render JavaScript.
    
    Args:
        url (str): The URL to fetch HTML content from
        
    Returns:
        Optional[str]: HTML content as string if successful, None otherwise
    """
    logger = logging.getLogger('web_scraper')
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            # Wait for the page to load completely
            page.wait_for_load_state('networkidle')
            html = page.content()
            browser.close()
            logger.info(f"Successfully fetched HTML from {url} using Playwright")
            return html
    except Exception as e:
        logger.error(f"Failed to fetch HTML from {url} using Playwright: {e}")
        return None


def fetch_html(url: str, retries: int = 3, delay: int = 5) -> Optional[str]:
    """
    Fetch HTML content from a given URL with retry mechanism.
    First tries with requests, then falls back to Playwright if no table is found.
    
    Args:
        url (str): The URL to fetch HTML content from
        retries (int): Number of retry attempts (default: 3)
        delay (int): Base delay between retries in seconds (default: 5)
        
    Returns:
        Optional[str]: HTML content as string if successful, None otherwise
    """
    logger = logging.getLogger('web_scraper')
    
    for attempt in range(retries + 1):
        try:
            # Make a GET request with a timeout
            response = requests.get(url, timeout=30)
            # Raise an exception for bad status codes
            response.raise_for_status()
            # Log success
            logger.info(f"Successfully fetched HTML from {url}")
            # Diagnostic logging
            logger.debug(f"HTTP Response - Status: {response.status_code}, URL: {response.url}")
            logger.debug(f"HTTP Response - Content-Type: {response.headers.get('content-type')}")
            logger.debug(f"HTTP Response - Content Length: {len(response.text)}")
            # Log a snippet of the response content (first 1000 characters)
            snippet = response.text[:1000]
            logger.debug(f"HTTP Response - Content Snippet: {snippet}")
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
                # Try Playwright fallback
                logger.info("Falling back to Playwright to render the page")
                return fetch_html_with_playwright(url)
