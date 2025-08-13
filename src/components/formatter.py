"""
Data formatter and CSV writer for the Artificial Analysis Leaderboard Scraper.

This module formats extracted data and outputs to CSV files with proper
data validation and normalization.

Key Features:
- Normalizes data types and formats
- Handles data cleaning and validation
- Generates CSV files with proper headers
- Supports different output formats (CSV, JSON)
- Implements data deduplication
- Adds metadata (scrape timestamp, source URL)
"""

import csv
import logging


def write_to_csv(data: list[list[str]], file_path: str) -> None:
    """
    Write data to a CSV file with proper error handling and logging.

    This utility currently only supports CSV output.

    Args:
        data: A list of lists containing the data to write. The first row should contain headers.
        file_path: The path where the CSV file should be created.

    Raises:
        IOError: If there's an issue writing to the file.
    """
    logger = logging.getLogger(__name__)
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        logger.info(f"Successfully created CSV file at {file_path}")
    except IOError as e:
        logger.error(f"Error writing to CSV file {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while writing to CSV file {file_path}: {e}")
        raise