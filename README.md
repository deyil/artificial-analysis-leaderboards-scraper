# Artificial Analysis Leaderboard Scraper

A Python web scraper designed to extract leaderboard data from the [Artificial Analysis website](https://artificialanalysis.ai/leaderboards/providers/prompt-options/single/medium_coding?deprecation=all) and save it to a CSV file.

## Features

- Extracts leaderboard data from Artificial Analysis website
- Handles HTTP requests with retry mechanism and exponential backoff
- Parses HTML content using Beautiful Soup 4
- Outputs data to CSV format with proper error handling
- Comprehensive logging for debugging and monitoring
- Configurable through YAML configuration file

## Project Structure

```
artificialanalysis-scraper/
├── src/
│   ├── __init__.py
│   ├── scraper.py          # Core HTTP request handling
│   ├── parser.py           # HTML parsing and data extraction
│   ├── formatter.py        # Data formatting and CSV output
│   ├── config.py           # Configuration settings
│   └── logger.py           # Logging configuration
├── specs/
│   ├── architecture.md     # Technical architecture document
│   ├── requirements.md     # Project requirements
│   └── tasks.md            # Implementation tasks
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_parser.py
│   └── test_formatter.py
├── data/
│   └── output/             # CSV output directory
├── logs/                   # Application logs
├── main.py                 # Entry point script
├── requirements.txt        # Python dependencies
├── config.yaml             # Configuration file
└── README.md               # Project documentation
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/artificialanalysis-scraper.git
   cd artificialanalysis-scraper
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scraper with:
```bash
python src/main.py
```

The scraper will:
1. Load configuration from `config.yaml`
2. Fetch HTML content from the target URL
3. Parse the leaderboard data from the HTML
4. Write the data to a CSV file

## Configuration

The scraper can be configured through the `config.yaml` file:

```yaml
target_url: "https://artificialanalysis.ai/leaderboards/providers/prompt-options/single/medium_coding?deprecation=all"
output_csv_path: "data/leaderboard.csv"
```

- `target_url`: The URL of the leaderboard to scrape
- `output_csv_path`: The path where the CSV output will be saved

## Components

### Scraper (`src/components/scraper.py`)
Handles HTTP communication with the target website:
- Makes GET requests to the leaderboard URL
- Implements retry logic with exponential backoff
- Handles HTTP errors and timeouts

### Parser (`src/components/parser.py`)
Parses HTML content and extracts structured data:
- Uses Beautiful Soup 4 for HTML parsing
- Identifies and extracts table headers dynamically
- Extracts data from table rows

### Formatter (`src/components/formatter.py`)
Formats extracted data and outputs to CSV:
- Writes data to CSV files with proper error handling
- Handles data validation
- Appends timestamp to output filenames in format _YYYYMMDD_HHMMSS

### Config (`src/components/config.py`)
Manages application configuration:
- Loads configuration from YAML file
- Validates configuration parameters

### Logger (`src/components/logger.py`)
Configures and manages application logging:
- Outputs to both console (DEBUG level) and file (INFO level)
- Uses structured logging format

## Logging

The scraper uses structured logging with multiple levels:
- Console output: DEBUG level
- File output (`logs/scraper.log`): INFO level

Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Error Handling

The scraper implements comprehensive error handling:
- Network errors: Retry mechanism with exponential backoff
- Parsing errors: Graceful handling of malformed data
- File I/O errors: Proper error reporting and handling

## Terminal Process Indicator

A terminal spinner has been added to provide real-time feedback during the Playwright rendering process. This feature uses the `rich` library to display a spinner in the terminal, indicating that the scraping process is in progress.

## Dependencies

- requests: HTTP library for Python
- beautifulsoup4: HTML parsing library
- pyyaml: YAML parser and emitter for Python
- rich: For displaying the terminal spinner

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request