"""
Configuration management for the Artificial Analysis Leaderboard Scraper.

This module manages application configuration and settings, loading
configuration from YAML files and providing default values.

Key Features:
- Loads configuration from YAML file
- Provides default values for all settings
- Supports environment variable overrides
- Validates configuration parameters
"""

import yaml
import logging
from typing import Dict, Any


def load_config(config_path: str = 'config.yaml') -> Dict[Any, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path (str): Path to the YAML configuration file. Defaults to 'config.yaml'.
        
    Returns:
        dict: Configuration dictionary loaded from the YAML file.
    """
    # Get logger instance
    logger = logging.getLogger('web_scraper')
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info(f"Configuration loaded successfully from {config_path}")
            
            # Validate required configuration keys
            required_keys = ['target_url', 'output_csv_path']
            for key in required_keys:
                if key not in config:
                    logger.critical(f"Missing required configuration key: {key}")
                    return {}
            
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file {config_path} not found")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {config_path}: {e}")
        return {}