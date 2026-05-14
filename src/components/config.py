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

import logging
import os
from typing import Any, Dict

import yaml


def _parse_bool(value: Any) -> bool:
    """Convert common config and environment values to a boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "off"}
    return bool(value)


def load_config(config_path: str = "config.yaml") -> Dict[Any, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path (str): Path to the YAML configuration file. Defaults to 'config.yaml'.

    Returns:
        dict: Configuration dictionary loaded from the YAML file.
    """
    # Get logger instance
    logger = logging.getLogger("web_scraper")

    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file) or {}
            logger.info(f"Configuration loaded successfully from {config_path}")

            config["output_add_timestamp"] = _parse_bool(
                config.get("output_add_timestamp", True)
            )

            # Check for environment variable overrides
            target_url_env = os.getenv("TARGET_URL")
            if target_url_env:
                config["target_url"] = target_url_env
                logger.info(
                    f"Overriding target_url with environment variable: {target_url_env}"
                )

            output_path_env = os.getenv("OUTPUT_PATH")
            if output_path_env:
                config["output_csv_path"] = output_path_env
                logger.info(
                    f"Overriding output_csv_path with environment variable: {output_path_env}"
                )

            output_add_timestamp_env = os.getenv("OUTPUT_ADD_TIMESTAMP")
            if output_add_timestamp_env is not None:
                config["output_add_timestamp"] = _parse_bool(
                    output_add_timestamp_env
                )
                logger.info(
                    "Overriding output_add_timestamp with environment variable: "
                    f"{config['output_add_timestamp']}"
                )

            # Validate required configuration keys
            required_keys = ["target_url", "output_csv_path"]
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
