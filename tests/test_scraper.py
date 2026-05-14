from unittest.mock import patch

from src.components.scraper import PlaywrightBrowserMissingError, fetch_html


def test_playwright_retries():
    """
    Test that fetch_html retries correctly when Playwright fails.
    """
    with patch(
        "src.components.scraper.fetch_html_with_playwright",
        side_effect=[
            None,  # First attempt fails
            None,  # Second attempt fails
            "<html><body>Success content</body></html>",  # Third attempt succeeds
        ],
    ) as mock_playwright:
        result = fetch_html("https://example.com", retries=2, delay=0)

        # Should have tried 3 times (0, 1, 2)
        assert mock_playwright.call_count == 3
        assert result is not None
        assert "Success content" in result


def test_playwright_backoff_sleeps_once_per_failed_attempt():
    with patch(
        "src.components.scraper.fetch_html_with_playwright",
        side_effect=[
            None,
            None,
            "<html><body>Success content</body></html>",
        ],
    ), patch("src.components.scraper.time.sleep") as mock_sleep:
        result = fetch_html("https://example.com", retries=2, delay=5)

    assert result is not None
    assert [call.args[0] for call in mock_sleep.call_args_list] == [5, 10]


def test_missing_playwright_browser_fails_without_retrying():
    with patch(
        "src.components.scraper.fetch_html_with_playwright",
        side_effect=PlaywrightBrowserMissingError("install required"),
    ) as mock_playwright, patch("src.components.scraper.time.sleep") as mock_sleep:
        result = fetch_html("https://example.com", retries=3, delay=5)

    assert result is None
    assert mock_playwright.call_count == 1
    mock_sleep.assert_not_called()
