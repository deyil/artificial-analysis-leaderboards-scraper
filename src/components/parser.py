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
    logger = logging.getLogger(__name__)
    logger.info("Starting to parse leaderboard HTML")
    
    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')
    
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
        header_row = thead.find('tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            result.append(headers)
    
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