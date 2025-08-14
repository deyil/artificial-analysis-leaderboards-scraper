import pytest
from unittest.mock import patch, MagicMock
import requests
from src.components.scraper import fetch_html

def test_playwright_fallback():
    """
    Test that fetch_html falls back to Playwright when requests fails with RequestException.
    """
    # Mock requests.get to raise a RequestException
    with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
        # Mock the Playwright fallback function to return a simple HTML string
        with patch('src.components.scraper.fetch_html_with_playwright') as mock_playwright:
            mock_playwright.return_value = "<html><body>Fallback content</body></html>"
            
            # Call the function under test
            result = fetch_html("https://example.com")
            
            # Assert that the Playwright fallback was called
            mock_playwright.assert_called_once_with("https://example.com")
            
            # Assert that fetch_html returned the fallback content (not None)
            assert result is not None
            assert "Fallback content" in result