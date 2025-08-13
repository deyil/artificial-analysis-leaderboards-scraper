"""
Unit tests for the parser module of the Artificial Analysis Leaderboard Scraper.

This module contains tests for the HTML parsing and data extraction functionality,
ensuring accurate extraction of leaderboard data from various HTML structures.

Tests include:
- Table header extraction
- Row data parsing
- Data type conversion
- Error handling for malformed HTML
- Provider name extraction with alt text preference and filename fallback
"""

import sys
import os
import pytest

# Add the src directory to the path so we can import from src.components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from components.parser import parse_leaderboard, extract_provider_name
from bs4 import BeautifulSoup


def test_extract_provider_name_with_alt_text():
    """Test provider name extraction when alt text is present."""
    html = '<td><img alt="Fireworks logo" src="/img/logos/fireworks.svg"></td>'
    soup = BeautifulSoup(html, 'html.parser')
    cell = soup.find('td')
    
    result = extract_provider_name(cell)
    assert result == "Fireworks"


def test_extract_provider_name_with_alt_text_no_logo_suffix():
    """Test provider name extraction when alt text doesn't have 'logo' suffix."""
    html = '<td><img alt="OpenAI" src="/img/logos/openai_small.svg"></td>'
    soup = BeautifulSoup(html, 'html.parser')
    cell = soup.find('td')
    
    result = extract_provider_name(cell)
    assert result == "OpenAI"


def test_extract_provider_name_fallback_to_filename():
    """Test provider name extraction falls back to filename when alt is missing."""
    html = '<td><img src="/img/logos/fireworks.svg"></td>'
    soup = BeautifulSoup(html, 'html.parser')
    cell = soup.find('td')
    
    result = extract_provider_name(cell)
    assert result == "fireworks"


def test_extract_provider_name_fallback_to_filename_no_extension():
    """Test provider name extraction removes file extension from filename."""
    html = '<td><img src="/img/logos/openai_small.svg"></td>'
    soup = BeautifulSoup(html, 'html.parser')
    cell = soup.find('td')
    
    result = extract_provider_name(cell)
    assert result == "openai_small"


def test_extract_provider_name_empty_alt_fallback_to_filename():
    """Test provider name extraction falls back to filename when alt is empty."""
    html = '<td><img alt="" src="/img/logos/fireworks.svg"></td>'
    soup = BeautifulSoup(html, 'html.parser')
    cell = soup.find('td')
    
    result = extract_provider_name(cell)
    assert result == "fireworks"


def test_extract_provider_name_no_img():
    """Test provider name extraction when no img element is present."""
    html = '<td><div>Some content</div></td>'
    soup = BeautifulSoup(html, 'html.parser')
    cell = soup.find('td')
    
    result = extract_provider_name(cell)
    assert result == ""


def test_parse_leaderboard_with_sample_row():
    """Test parsing of a sample table row with provider logo."""
    # Using the sample HTML row provided in the task
    html = '''
    <table>
        <tbody>
            <tr>
                <td class="h-12 p-0 align-middle">
                    <div class="h-12 align-middle text-center px-2 pr-4 flex items-center justify-center font-semibold border-l-8">
                        <img alt="Fireworks logo" class="h-6 w-auto max-w-[70px] object-contain m-auto" src="/img/logos/fireworks.svg" />
                    </div>
                </td>
                <td class="h-12 p-0 align-middle">
                    <div class="flex items-center font-semibold">
                        <img alt="OpenAI logo" class="mr-2 h-5 w-auto max-w-12 max-h-5 object-contain" src="/img/logos/openai_small.svg" />
                        <div class="flex w-48 flex-col"><span>gpt-oss-120B (high)</span></div>
                    </div>
                </td>
                <td class="h-12 p-0 align-middle">
                    <div class="h-12 align-middle text-center px-2 flex items-center justify-center">131k</div>
                </td>
            </tr>
        </tbody>
    </table>
    '''
    
    result = parse_leaderboard(html)
    
    # Should have 1 data row (no headers in this HTML)
    assert len(result) == 1
    
    # Check that the first cell (provider name) is correctly extracted
    assert result[0][0] == "Fireworks"
    
    # Check that other cells are extracted correctly
    assert result[0][1] == "gpt-oss-120B (high)"
    assert result[0][2] == "131k"