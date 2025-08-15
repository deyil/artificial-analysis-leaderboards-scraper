from unittest.mock import patch
from src.components.scraper import fetch_html

def test_playwright_retries():
    """
    Test that fetch_html retries correctly when Playwright fails.
    """
    with patch('src.components.scraper.fetch_html_with_playwright', side_effect=[
        None,  # First attempt fails
        None,  # Second attempt fails
        "<html><body>Success content</body></html>"  # Third attempt succeeds
    ]) as mock_playwright:
        result = fetch_html("https://example.com", retries=2, delay=0)
        
        # Should have tried 3 times (0, 1, 2)
        assert mock_playwright.call_count == 3
        assert result is not None
        assert "Success content" in result