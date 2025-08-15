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
import random
from rich.console import Console

console = Console()

# List of common User-Agent strings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
]

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
        with console.status("[bold green]Rendering page with Playwright...", spinner="dots") as status:
            with sync_playwright() as p:
                status.update("Launching browser...")
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                # Set a random User-Agent for Playwright
                page.set_extra_http_headers({
                    "User-Agent": random.choice(USER_AGENTS)
                })
                status.update("Navigating to page...")
                page.goto(url)
                status.update("Waiting for page to load...")
                # Wait for the page to load completely
                page.wait_for_load_state('networkidle')

                if click_header_buttons:
                    status.update("Clicking headers...")
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
                status.update("Extracting HTML...")
                html = page.content()
                browser.close()
                logger.info(f"Successfully fetched HTML from {url} using Playwright")
                return html
    except Exception as e:
        logger.error(f"Failed to fetch HTML from {url} using Playwright: {e}")
        return None


def fetch_html(url: str, retries: int = 3, delay: int = 5) -> Optional[str]:
    """
    Fetch HTML content from a given URL using Playwright as the primary method.
    
    Args:
        url (str): The URL to fetch HTML content from
        retries (int): Number of retry attempts (default: 3)
        delay (int): Base delay between retries in seconds (default: 5)
        
    Returns:
        Optional[str]: HTML content as string if successful, None otherwise
    """
    logger = logging.getLogger('web_scraper')
    
    for attempt in range(retries + 1):
        # Implement rate-limiting with exponential backoff
        if attempt > 0:
            min_delay = 1
            time.sleep(max(min_delay, delay * (2 ** (attempt-1))))
        
        html = fetch_html_with_playwright(url)
        if html is not None:
            return html
        
        if attempt < retries:
            backoff_delay = delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed fetching HTML from {url} with Playwright. Retrying in {backoff_delay} seconds...")
            time.sleep(backoff_delay)
        else:
            logger.error(f"Failed to fetch HTML from {url} after {retries + 1} attempts with Playwright")
            return None
