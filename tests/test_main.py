from unittest.mock import patch, MagicMock, call

def test_main_orchestration_calls_in_order():
    """
    Integration-style test for the main orchestration flow.

    This test patches the core functions used inside src.main.main() and
    records the sequence in which they are invoked. It asserts the expected
    order and verifies each function was called with expected args.
    """
    seq = MagicMock()

    with patch('src.main.setup_logger') as mock_setup_logger, \
         patch('src.main.load_config') as mock_load_config, \
         patch('src.main.fetch_html') as mock_fetch_html, \
         patch('src.main.parse_leaderboard') as mock_parse_leaderboard, \
         patch('src.main.fetch_html_with_playwright') as mock_fetch_playwright, \
         patch('src.main.write_to_csv') as mock_write_to_csv:

        # Record logger setup
        mock_setup_logger.side_effect = lambda: seq('setup_logger')

        # load_config returns required keys
        def _load_config():
            seq('load_config')
            return {
                'target_url': 'https://example.com',
                'output_csv_path': '/tmp/out.csv'
            }
        mock_load_config.side_effect = _load_config

        # fetch_html returns simple HTML
        def _fetch_html(url):
            seq('fetch_html')
            return '<html>content</html>'
        mock_fetch_html.side_effect = _fetch_html

        # parse_leaderboard returns a non-empty dataset
        def _parse(html):
            seq('parse_leaderboard')
            return [['Header1'], ['Row1']]
        mock_parse_leaderboard.side_effect = _parse

        # Playwright fallback should not be used in this happy path, but record if it is
        mock_fetch_playwright.side_effect = lambda url: (seq('fetch_html_with_playwright'), None)[1]

        # write_to_csv should be called last
        def _write(data, path):
            seq('write_to_csv')
        mock_write_to_csv.side_effect = _write

        # Import and run main while the names in src.main are patched
        from src.main import main
        main()

    # Verify the sequence of operations
    expected_sequence = [
        call('setup_logger'),
        call('load_config'),
        call('fetch_html'),
        call('parse_leaderboard'),
        call('write_to_csv'),
    ]
    seq.assert_has_calls(expected_sequence, any_order=False)

    # Additional assertions on individual mock calls and args
    mock_load_config.assert_called_once()
    mock_fetch_html.assert_called_once_with('https://example.com')
    mock_parse_leaderboard.assert_called_once_with('<html>content</html>')
    mock_write_to_csv.assert_called_once_with([['Header1'], ['Row1']], '/tmp/out.csv')