
# Email Scraper Script

This script scrapes email addresses from a list of URLs provided in a CSV file. It also allows for email enrichment using the Hunter.io API and supports converting JSON output to CSV format.

## Features

- Scrapes email addresses from URLs.
- Follows "contact" links to find additional emails.
- Enriches email data using Hunter.io API (if configured).
- Handles URLs without HTTP/HTTPS schema.
- Logs all actions, errors, and progress.
- Supports converting JSON output to CSV format.
- Excludes emails with blacklisted file extensions (e.g., .jpg, .png).

## Requirements

- Python 3.6 or higher
- Playwright
- Requests

## Installation

1. **Install required Python packages:**
    ```sh
    pip install playwright requests
    playwright install
    ```

2. **Clone the repository and navigate to the directory:**
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

3. **Replace `your_hunter_api_key` in `config.json` with your actual Hunter API key.**

## Usage

### Scraping Emails

To scrape emails from URLs provided in a CSV file:

```sh
python email_scraper.py input.csv -o csv
```

- `input.csv`: The input CSV file containing URLs.
- `-o csv`: Specifies the output format. Options are `json` (default) or `csv`.

### Converting JSON to CSV

To convert a JSON output file to CSV format:

```sh
python email_scraper.py -convert input.json
```

- `-convert`: Flag to indicate conversion from JSON to CSV.
- `input.json`: The JSON file to be converted.

### Configuration

The script uses a `config.json` file for configuration:

```json
{
    "api_key": "your_hunter_api_key",
    "use_hunter": true,
    "wait_time": 1
}
```

- `api_key`: Your Hunter.io API key.
- `use_hunter`: Boolean flag to enable or disable Hunter.io enrichment.
- `wait_time`: Time in seconds to wait between requests.

## Logging

The script generates a log file with a name in the format `email-scrape-log-YYYY-MM-DD.log`. It logs all actions, errors, and progress with timestamps and status codes.

## Example Files

### `input.csv`
```csv
urls
https://example.com
http://testsite.com
```

### `config.json`
```json
{
    "api_key": "your_hunter_api_key",
    "use_hunter": true,
    "wait_time": 1
}
```

### `example_output.json`
```json
{
    "example.com": [
        {
            "value": "contact@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "position": "Manager",
            "confidence": 95
        },
        {
            "value": "info@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "position": "Director",
            "confidence": 90
        }
    ],
    "testsite.com": [
        {
            "value": "admin@testsite.com",
            "first_name": "Alice",
            "last_name": "Smith",
            "position": "Admin",
            "confidence": 92
        },
        {
            "value": "support@testsite.com",
            "first_name": "Bob",
            "last_name": "Brown",
            "position": "Support",
            "confidence": 88
        }
    ]
}
```

### `example_output.csv`
```csv
domain,email,first_name,last_name,position,confidence
example.com,contact@example.com,John,Doe,Manager,95
example.com,info@example.com,Jane,Doe,Director,90
testsite.com,admin@testsite.com,Alice,Smith,Admin,92
testsite.com,support@testsite.com,Bob,Brown,Support,88
```

## Notes

- Ensure that the `config.json` file is correctly configured with your Hunter.io API key if you want to use the email enrichment feature.
- The script gracefully handles errors and logs all issues to help with troubleshooting.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
