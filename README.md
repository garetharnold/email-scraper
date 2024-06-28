# Email Scraper Script

## Overview
This script is designed to scrape email addresses from a list of URLs provided in a CSV file. It is equipped with robust features to extract emails from both HTML source and rendered content, follow contact page links, and enrich data using the Hunter.io API. Additionally, it supports structured data extraction and customizable settings via a configuration file.

```
python3 orchestrator.py (shows possible args)
python3 orchestrator.py input.csv 
```

## Features

### Core Features:
1. **Email Scraping:**
   - Extracts email addresses from the provided URLs.

2. **Contact Page Discovery:**
   - Uses keywords to find and follow links to contact pages.

3. **HTML Source and Rendered Content Analysis:**
   - Scrapes email addresses from both the HTML source and the rendered content of web pages.

4. **Hunter.io API Integration:**
   - Enriches email data using the Hunter.io API if configured.

5. **Schema.org Parsing:**
   - Extracts organization information from schema.org structured data.

6. **Blacklist Filtering:**
   - Excludes emails with specific blacklisted file extensions.

7. **Output Formats:**
   - Supports both JSON and CSV output formats.

8. **Logging:**
   - Logs all actions, errors, and progress with timestamps for easy debugging and monitoring.

### Enhanced Features:
1. **Improved Error Handling:**
   - Implements detailed error logging to capture specific issues during scraping.

2. **Timeout and Retry Logic:**
   - Configurable timeout settings for page loads and retry logic to handle temporary failures.

3. **SSL Certificate Handling:**
   - Options to ignore SSL certificate errors.

4. **User-Agent Rotation:**
   - Rotates user-agents to mimic different browsers and avoid detection.

## Use Cases
- **Lead Generation:**
  - Automatically scrape email addresses from industry websites for building a leads database.
  
- **Market Research:**
  - Gather contact information from competitor or industry websites.

- **Data Enrichment:**
  - Use the Hunter.io API to enrich email data with additional information such as names and positions.

- **Web Monitoring:**
  - Monitor and collect contact information from multiple websites for outreach purposes.

## Configuration
The script uses a `config.json` file for configuration, allowing customization of various settings:

### Configuration Options:

- **Scraping Settings:**
  - `wait_time`: Time to wait between requests to avoid getting blocked.
  - `timeout`: Maximum time to wait for a page to load.
  - `retry_attempts`: Number of retry attempts for failed requests.

- **Search Keywords:**
  - `contact_keywords`: List of keywords to look for in URLs or link texts to identify contact pages.

- **Output Settings:**
  - `enable_csv`: Boolean to enable CSV output in addition to JSON.
  - `enable_schema_crawling`: Boolean to enable or disable schema.org structured data crawling.

- **API Keys:**
  - `use_hunter`: Boolean to determine whether to use the Hunter API for email enrichment.
  - `hunter_api_key`: API key for the Hunter API.

- **Logging Settings:**
  - `log_levels`: A dictionary of log levels with boolean values to enable or disable each level.

- **HTML Parsing:**
  - `email_patterns`: List of regular expressions for email patterns to detect different email formats.

- **Blacklisted Filetypes:**
  - `blacklisted_filetypes`: List of file extensions to exclude when validating email addresses.

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

- Ensure that the `config.json` file is correctly configured with your [Hunter.io API](https://hunter.io/) key if you want to use the email enrichment feature.
- The script gracefully handles errors and logs all issues to help with troubleshooting.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
