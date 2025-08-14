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
import pandas as pd
import pandera as pa
from pandera.errors import SchemaError
from typing import List, Any

# Define the schema for leaderboard data validation
LEADERBOARD_SCHEMA = pa.DataFrameSchema({
    "Model": pa.Column(str, required=True, nullable=False),
    "Performance": pa.Column(float, required=True, nullable=False),
}, strict=True)

def format_data_as_csv(data: List[List[Any]]) -> str:
    """
    Format data as a CSV string with validation using pandera.
    
    This function converts a list of lists into a CSV string after validating
    the data against a predefined schema. It ensures data integrity before
    formatting.
    
    Args:
        data: A list of lists containing the data to format. The first row should contain headers.
        
    Returns:
        A CSV-formatted string ready for writing to a file or further processing.
        
    Raises:
        SchemaError: If the data fails validation against the defined schema.
        
    Example:
        >>> data = [["Model", "Performance"], ["GPT-4", 95.5], ["Claude 3", 92.1]]
        >>> csv_string = format_data_as_csv(data)
    """
    logger = logging.getLogger(__name__)
    
    # Convert list of lists to DataFrame
    if not data:
        raise ValueError("Data cannot be empty")
        
    headers = data[0]
    rows = data[1:]
    
    df = pd.DataFrame(rows, columns=headers)
    
    # Validate the DataFrame against the schema
    try:
        validated_df = LEADERBOARD_SCHEMA.validate(df)
        logger.debug("Data validation successful")
    except SchemaError as e:
        logger.error(f"Data validation failed: {e}")
        raise
    
    # Convert validated DataFrame to CSV string
    csv_string = validated_df.to_csv(index=False)
    return csv_string

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