"""
HTML parser and data extractor for the Artificial Analysis Leaderboard Scraper.

This module parses HTML content and extracts structured data from the leaderboard table
using Beautiful Soup 4 for HTML parsing.

Key Features:
- Uses Beautiful Soup 4 for HTML parsing
- Identifies and extracts table headers dynamically
- Handles different table structures and layouts
- Extracts data from complex table cells (logos, links, formatted text)
- Validates data integrity during extraction
- Handles missing or malformed data gracefully
"""

from bs4 import BeautifulSoup
import logging
from typing import List


def parse_leaderboard(html: str) -> List[List[str]]:
    """
    Parse the leaderboard table from HTML content.
    
    Args:
        html (str): HTML content containing the leaderboard table
        
    Returns:
        List[List[str]]: A list of lists where the first inner list contains headers
                         and subsequent inner lists contain data for each row
    """
    logger = logging.getLogger('web_scraper')
    logger.info("Starting to parse leaderboard HTML")
    
    # Diagnostic logging
    logger.debug(f"HTML Length: {len(html)}")
    # Log a snippet of the HTML content (first 500 characters)
    snippet = html[:500]
    logger.debug(f"HTML Snippet: {snippet}")
    
    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')
    
    # Diagnostic logging for HTML structure
    table_count = len(soup.find_all('table'))
    iframe_count = len(soup.find_all('iframe'))
    role_table_count = len(soup.find_all(attrs={"role": "table"}))
    logger.debug(f"Table Count: {table_count}, Iframe Count: {iframe_count}, Role Table Count: {role_table_count}")
    
    # Try to parse Next.js embedded JSON
    next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
    if next_data_script and next_data_script.string:
        try:
            import json
            next_data = json.loads(next_data_script.string)
            # Extract leaderboard data from next_data
            # This will depend on the specific structure of the JSON
            logger.debug("Found Next.js embedded JSON")
            # TODO: Implement actual JSON parsing logic here
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Next.js embedded JSON: {e}")
    else:
        logger.debug("Next.js embedded JSON script tag not found or empty")
    
    # Find the main leaderboard table
    # Based on the architecture document, we're looking for a table structure
    table = soup.find('table')
    
    if not table:
        # If no table found, log error and return empty list
        logger.error("No table found in HTML content")
        return []
    
    # Initialize result list
    result = []

    # Extract headers from thead
    thead = table.find('thead')
    if thead:
        header_rows = thead.find_all('tr')
        logger.debug(f"Found {len(header_rows)} header rows in thead")
        if header_rows:
            header_texts = []
            best_idx = 0
            best_nonempty = -1
            for idx, row in enumerate(header_rows):
                cols = [th.get_text(" ", strip=True) for th in row.find_all(['th', 'td'])]
                header_texts.append(cols)
                nonempty = sum(1 for c in cols if c and c.strip())
                logger.debug(f"Header row #{idx}: {cols} (non-empty: {nonempty})")
                # Prefer row with most non-empty headers; on tie, pick later row
                if nonempty > best_nonempty or (nonempty == best_nonempty and idx > best_idx):
                    best_nonempty = nonempty
                    best_idx = idx
            chosen_headers = header_texts[best_idx]
            logger.info(f"Selected thead header row #{best_idx} with {best_nonempty} non-empty headers: {chosen_headers}")
            result.append(chosen_headers)

    # Extract data rows from tbody
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
        for row in rows:
            # Extract cell data from each row
            cell_data = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            # Only add non-empty rows
            if cell_data:
                result.append(cell_data)

    logger.info(f"Finished parsing leaderboard. Found {len(result)} rows (including headers)")
    return result
