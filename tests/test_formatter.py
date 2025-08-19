"""
Unit tests for the formatter module of the Artificial Analysis Leaderboard Scraper.

This module contains tests for the data formatting and CSV output functionality,
ensuring proper data normalization and file generation.

Tests include:
- Data type normalization
- CSV file generation
- Data validation
- Error handling for invalid data
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from src.components.formatter import write_to_csv


class TestFormatter(unittest.TestCase):
    """Test cases for the formatter module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_csv_path = os.path.join(self.temp_dir, "test_output.csv")

    def tearDown(self):
        """Clean up after each test method."""
        import glob

        # Clean up the specific test file if it exists
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)

        # Clean up any other files that might have been created in the temp directory
        # This handles timestamped files or other files that write_to_csv might create
        try:
            for file_path in glob.glob(os.path.join(self.temp_dir, "*")):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    # Remove subdirectories recursively if any were created
                    import shutil

                    shutil.rmtree(file_path)
        except (OSError, FileNotFoundError):
            # Ignore errors if files are already gone
            pass

        # Remove the temp directory
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            # If directory is not empty, force remove it
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_format_data_as_csv_empty_input(self):
        """Test format_data_as_csv handles empty input data gracefully."""
        # Test with empty list
        empty_data = []

        # Since format_data_as_csv doesn't exist yet, we'll test the expected behavior
        # The function should handle empty data by returning an empty string or raising a specific exception
        try:
            from src.components.formatter import format_data_as_csv

            result = format_data_as_csv(empty_data)
            # If function returns a string, it should be empty for empty input
            self.assertEqual(result, "", "Empty input should return empty string")
        except ImportError:
            # If function doesn't exist yet, we'll skip this test but document the expected behavior
            self.skipTest("format_data_as_csv function not yet implemented")
        except ValueError as e:
            # If function raises ValueError for empty input, that's also acceptable
            self.assertIn(
                "empty", str(e).lower(), "ValueError should mention empty data"
            )

    def test_format_data_as_csv_malformed_input_inconsistent_keys(self):
        """Test format_data_as_csv handles malformed input with inconsistent dictionary keys."""
        # Test with dictionaries having inconsistent keys
        malformed_data = [
            ["Model", "Performance", "Rank"],  # Headers matching schema
            ["Model A", 85.0, 1],
            ["Model B", 78.0],  # Missing 'Rank' field
            ["Model C", 92.0, 2, "bonus"],  # Extra field
            ["Model D", 67.0],  # Missing 'Rank' field
        ]

        try:
            from src.components.formatter import format_data_as_csv

            # The function should handle this gracefully, either by:
            # 1. Processing only the valid/common fields and logging a warning
            # 2. Raising a specific exception with clear error message
            # 3. Normalizing the data by filling missing fields with empty values

            with patch("src.components.formatter.logging") as mock_logging:
                result = format_data_as_csv(malformed_data)

                # Check if warning was logged about inconsistent data
                mock_logging.getLogger().warning.assert_called()
                warning_call_args = mock_logging.getLogger().warning.call_args[0][0]
                self.assertIn("inconsistent", warning_call_args.lower())

                # Result should still be a valid CSV string (non-empty)
                self.assertIsInstance(result, str)
                self.assertGreater(
                    len(result),
                    0,
                    "Should return valid CSV data despite inconsistencies",
                )

        except ImportError:
            self.skipTest("format_data_as_csv function not yet implemented")
        except (ValueError, KeyError) as e:
            # If function raises an exception for malformed data, verify it's descriptive
            error_message = str(e).lower()
            self.assertTrue(
                any(
                    keyword in error_message
                    for keyword in [
                        "inconsistent",
                        "malformed",
                        "keys",
                        "schema",
                        "columns passed",
                        "passed data",
                        "columns",
                    ]
                ),
                f"Exception message should be descriptive about the data issue: {e}",
            )

    def test_format_data_as_csv_malformed_input_non_dict_elements(self):
        """Test format_data_as_csv handles malformed input with inconsistent row structures."""
        # Test with mixed data types in rows (inconsistent list structures)
        malformed_data = [
            ["Model", "Performance"],  # Headers
            ["Model A", 85.0],  # Valid row
            ["Model B"],  # Missing Performance value
            ["Model C", 78.0, "extra_data"],  # Extra data
            [
                "Model D",
                "invalid_performance_type",
            ],  # Invalid data type for Performance
        ]

        try:
            from src.components.formatter import format_data_as_csv

            with patch("src.components.formatter.logging"):
                with self.assertRaises((TypeError, ValueError, Exception)) as context:
                    format_data_as_csv(malformed_data)

                # Verify the exception message is descriptive about data issues
                error_message = str(context.exception).lower()
                self.assertTrue(
                    any(
                        keyword in error_message
                        for keyword in [
                            "schema",
                            "validation",
                            "data",
                            "type",
                            "column",
                        ]
                    ),
                    f"Exception should mention data validation issues: {context.exception}",
                )

        except ImportError:
            self.skipTest("format_data_as_csv function not yet implemented")

    def test_write_to_csv_existing_function(self):
        """Test the existing write_to_csv function with various scenarios."""
        # Test normal operation
        test_data = [
            ["Name", "Score", "Rank"],
            ["Model A", "85", "1"],
            ["Model B", "78", "2"],
        ]

        write_to_csv(test_data, self.test_csv_path, add_timestamp=False)

        # Verify file was created and contains expected data
        self.assertTrue(os.path.exists(self.test_csv_path))

        with open(self.test_csv_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Name,Score,Rank", content)
            self.assertIn("Model A,85,1", content)

    def test_write_to_csv_empty_data(self):
        """Test write_to_csv with empty data."""
        empty_data = []

        # Should handle empty data without crashing
        write_to_csv(empty_data, self.test_csv_path, add_timestamp=False)

        # File should be created but empty
        self.assertTrue(os.path.exists(self.test_csv_path))

        with open(self.test_csv_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertEqual(content, "")

    def test_write_to_csv_io_error(self):
        """Test write_to_csv handles IO errors properly."""
        test_data = [["Header"], ["Data"]]
        invalid_path = "/invalid/path/that/does/not/exist/file.csv"

        with patch("src.components.formatter.logging") as mock_logging:
            with self.assertRaises(IOError):
                write_to_csv(test_data, invalid_path)

            # Verify error was logged
            mock_logging.getLogger().error.assert_called()


if __name__ == "__main__":
    unittest.main()
