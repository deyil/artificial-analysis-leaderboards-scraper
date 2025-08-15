import pytest
from src.components import scraper


class DummyStatusCM:
    def __init__(self, console, initial_message, spinner=None):
        self.console = console
        self.initial_message = initial_message
        self.spinner = spinner

    def __enter__(self):
        # Record that status() was entered and capture initial args
        self.console.status_calls.append((self.initial_message, self.spinner))
        self.console.entered = True
        return self

    def update(self, message):
        # Record each status.update() call in order
        self.console.status_updates.append(message)

    def __exit__(self, exc_type, exc, tb):
        self.console.exited = True
        return False


class DummyConsole:
    def __init__(self):
        self.status_calls = []
        self.status_updates = []
        self.entered = False
        self.exited = False

    def status(self, message, spinner=None, **kwargs):
        # Return the context manager object used as `status` in the scraper
        return DummyStatusCM(self, message, spinner)


# --- Mocks for Playwright objects --- #
class MockButton:
    def __init__(self):
        self.clicked = False

    def is_visible(self):
        return True

    def is_enabled(self):
        return True

    def click(self):
        self.clicked = True


class MockHeaderButtons:
    def __init__(self, count):
        self._count = count
        self._buttons = [MockButton() for _ in range(count)]

    def count(self):
        return self._count

    def nth(self, i):
        return self._buttons[i]


class MockPage:
    def __init__(self, html, header_button_count=0):
        self._html = html
        self._header_buttons = MockHeaderButtons(header_button_count)
        self.headers_set = None
        self.url = None
        self.load_state = None
        self.timeout_waited = None

    def set_extra_http_headers(self, headers):
        self.headers_set = headers

    def goto(self, url):
        self.url = url

    def wait_for_load_state(self, state):
        self.load_state = state

    def wait_for_timeout(self, ms):
        self.timeout_waited = ms

    def locator(self, selector):
        # Return the mock header buttons object
        return self._header_buttons

    def content(self):
        return self._html


class MockBrowser:
    def __init__(self, page):
        self._page = page
        self.closed = False

    def new_page(self):
        return self._page

    def close(self):
        self.closed = True


class MockChromium:
    def __init__(self, page):
        self._page = page

    def launch(self, headless=True):
        return MockBrowser(self._page)


class MockPlaywright:
    def __init__(self, page):
        self.chromium = MockChromium(page)


class MockSyncPlaywrightCM:
    def __init__(self, page):
        self.page = page

    def __enter__(self):
        return MockPlaywright(self.page)

    def __exit__(self, exc_type, exc, tb):
        return False


def make_mock_sync_playwright(html, header_button_count=0):
    """
    Factory that returns a mock sync_playwright function and the underlying mock page.
    The returned function can be monkeypatched in place of scraper.sync_playwright.
    """
    page = MockPage(html, header_button_count)

    def _mock_sync_playwright():
        return MockSyncPlaywrightCM(page)

    return _mock_sync_playwright, page


def test_spinner_updates_and_returns_html(monkeypatch):
    """
    Verify that console.status() is called, status.update() messages are emitted
    in the correct order, and the returned HTML matches the mock page content.
    """
    dummy_console = DummyConsole()
    monkeypatch.setattr(scraper, "console", dummy_console)

    expected_html = "<html><body>Test Page</body></html>"
    mock_sync, page = make_mock_sync_playwright(expected_html, header_button_count=2)
    monkeypatch.setattr(scraper, "sync_playwright", mock_sync)

    result = scraper.fetch_html_with_playwright("http://example.com")

    # Returned HTML matches mock page content
    assert result == expected_html

    # console.status() was called exactly once with expected initial message and spinner
    assert len(dummy_console.status_calls) == 1
    initial_msg, spinner = dummy_console.status_calls[0]
    assert initial_msg.startswith("[bold green]Rendering page with Playwright")
    assert spinner == "dots"

    # status.update() messages were called in the expected sequence
    assert dummy_console.status_updates == [
        "Launching browser...",
        "Navigating to page...",
        "Waiting for page to load...",
        "Clicking headers...",
        "Extracting HTML...",
    ]

    # Context manager enter/exit should have been invoked
    assert dummy_console.entered is True
    assert dummy_console.exited is True


def test_spinner_skips_clicks_when_disabled(monkeypatch):
    """
    When click_header_buttons is False we should not see the "Clicking headers..."
    update call, but other updates should still appear.
    """
    dummy_console = DummyConsole()
    monkeypatch.setattr(scraper, "console", dummy_console)

    expected_html = "<html><body>No Clicks</body></html>"
    mock_sync, page = make_mock_sync_playwright(expected_html, header_button_count=1)
    monkeypatch.setattr(scraper, "sync_playwright", mock_sync)

    result = scraper.fetch_html_with_playwright("http://example.com", click_header_buttons=False)

    assert result == expected_html

    # Ensure "Clicking headers..." is not present when disabled
    assert "Clicking headers..." not in dummy_console.status_updates

    # Other updates still occur in order before skipping clicks
    assert dummy_console.status_updates[:3] == [
        "Launching browser...",
        "Navigating to page...",
        "Waiting for page to load...",
    ]

    assert dummy_console.entered is True
    assert dummy_console.exited is True