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
import os


def extract_provider_name(cell) -> str:
    """
    Extract provider name from the first cell of a table row.
    
    Args:
        cell: BeautifulSoup element representing the first cell of a table row
        
    Returns:
        str: Provider name extracted from the cell
    """
    # Look for img element in the cell
    img = cell.find('img')
    if img:
        # Prefer alt attribute if it exists and is not empty
        alt_text = img.get('alt', '').strip()
        if alt_text:
            # Remove " logo" suffix if present
            if alt_text.lower().endswith(' logo'):
                return alt_text[:-5].strip()
            return alt_text
        
        # Fall back to src attribute filename without extension
        src = img.get('src', '').strip()
        if src:
            # Get basename (filename) from path
            filename = os.path.basename(src)
            # Remove file extension
            name_without_ext = os.path.splitext(filename)[0]
            return name_without_ext
    
    # If no img or no usable attributes, return empty string
    return ''


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
    
    # Try to parse Next.js embedded JSON
    soup = BeautifulSoup(html, 'html.parser')
    
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
    headers_found = False
    if thead:
        header_rows = thead.find_all('tr')
        logger.debug(f"Found {len(header_rows)} header rows in thead")
        if header_rows:
            header_texts = []
            for idx, row in enumerate(header_rows):
                cols = [th.get_text(" ", strip=True) for th in row.find_all(['th', 'td'])]
                header_texts.append(cols)

            # Step 1: Look for explicitly labeled headers (case-insensitive)
            known_header_patterns = ['model', 'performance', 'score', 'rank', 'provider', 'name', 'accuracy']
            best_idx = -1
            best_score = -1
            
            for idx, headers in enumerate(header_texts):
                # Convert headers to lowercase for comparison
                lower_headers = [h.lower() for h in headers if h]
                # Count how many known patterns are present
                score = sum(1 for pattern in known_header_patterns if any(pattern in header for header in lower_headers))
                if score > best_score:
                    best_score = score
                    best_idx = idx

            # Step 2: If no good match found, choose row with fewest empty cells and most unique non-empty headers
            if best_idx == -1:
                best_idx = 0
                best_quality = -1
                for idx, headers in enumerate(header_texts):
                    non_empty_count = sum(1 for h in headers if h and h.strip())
                    unique_count = len(set(h.lower() for h in headers if h and h.strip()))
                    empty_count = len(headers) - non_empty_count
                    # Quality score: prioritize more unique non-empty headers and fewer empty cells
                    quality = unique_count - empty_count
                    if quality > best_quality:
                        best_quality = quality
                        best_idx = idx

            chosen_headers = header_texts[best_idx]
            logger.info(f"Selected thead header row #{best_idx} with quality score: {best_score if best_score > -1 else best_quality}. Headers: {chosen_headers}")
            result.append(chosen_headers)
            headers_found = True

    # Step 3: Fallback if no headers found in thead
    header_row_index = None  # Track which row index was used as headers
    if not headers_found:
        # Look for the first non-empty row in tbody
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row_idx, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                cell_data = []
                for idx, cell in enumerate(cells):
                    if idx == 0:  # First cell contains provider logo
                        provider_name = extract_provider_name(cell)
                        cell_data.append(provider_name)
                    else:
                        cell_data.append(cell.get_text(strip=True))
                
                # If we found a row with meaningful content, use it as headers and generate safe column names
                if cell_data and any(cell_data):
                    # Generate safe placeholder column names
                    headers = []
                    for i, cell in enumerate(cell_data):
                        if cell.strip():
                            headers.append(cell.strip())
                        else:
                            headers.append(f'column_{i+1}')
                    result.append(headers)
                    header_row_index = row_idx  # Remember which row we used as headers
                    logger.info(f"Used first non-empty row as headers: {headers}")
                    headers_found = True
                    break

    # Extract data rows from tbody
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
        for row_idx, row in enumerate(rows):
            # Skip the row that was used as headers
            if header_row_index is not None and row_idx == header_row_index:
                continue
                
            # Extract cell data from each row
            cells = row.find_all(['td', 'th'])
            cell_data = []
            for idx, cell in enumerate(cells):
                if idx == 0:  # First cell contains provider logo
                    provider_name = extract_provider_name(cell)
                    cell_data.append(provider_name)
                else:
                    cell_data.append(cell.get_text(strip=True))
            
            # Only add rows that have meaningful content (not all empty cells)
            if cell_data and any(cell_data):
                result.append(cell_data)

    logger.info(f"Finished parsing leaderboard. Found {len(result)} rows (including headers)")
    return result
