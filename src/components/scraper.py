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


def fetch_html_with_playwright(url: str, click_header_buttons: bool = True) -> Optional[str]:
    """
    Fetch HTML content from a given URL using Playwright to render JavaScript.

    Args:
        url (str): The URL to fetch HTML content from
        click_header_buttons (bool): If True, attempt to click all buttons found in thead elements
                                    first <tr> to expand column headers before extracting HTML.

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

            if click_header_buttons:
                try:
                    header_buttons = page.locator('thead tr:first-of-type button')
                    btn_count = header_buttons.count()
                    logger.info(f"Found {btn_count} header buttons in thead; attempting to click them")
                    for i in range(btn_count):
                        btn = header_buttons.nth(i)
                        try:
                            # Only click if visible/enabled
                            if btn.is_visible() and btn.is_enabled():
                                btn.click()
                                logger.debug(f"Clicked header button #{i}")
                                # Small wait to allow DOM updates to settle
                                page.wait_for_timeout(200)
                            else:
                                logger.debug(f"Skipping header button #{i} (not visible or not enabled)")
                        except Exception as click_exc:
                            logger.warning(f"Error clicking header button #{i}: {click_exc}")
                except Exception as e:
                    logger.warning(f"Failed to locate or click header buttons: {e}")

            # Give the page a brief moment to update after clicks
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
