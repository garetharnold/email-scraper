# Email Scraper Script

## Overview
This script is designed to scrape email addresses from a list of URLs provided in a CSV file. It is equipped with robust features to extract emails from both HTML source and rendered content, follow contact page links, and enrich data using the Hunter.io API. Additionally, it supports structured data extraction and customizable settings via a configuration file.

## Usage
To run the script, use the following commands:

``` 
# Shows possible arguments
python3 orchestrator.py --help          

# Runs the scraper with the provided input CSV file
python3 orchestrator.py input.csv       
```

### Example Usage:
``` 
# Runs the scraper and outputs in JSON format (default)
python3 orchestrator.py input.csv -o json 

# Runs the scraper and outputs in CSV format
python3 orchestrator.py input.csv -o csv   

# Converts existing JSON file to CSV format
python3 orchestrator.py input.csv --convert    

# Runs the scraper ignoring SSL certificate errors
python3 orchestrator.py input.csv --ignore-certificate-errors  
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
   - Not implemented yet.

5. **Stop/Start Nature:**
   - The script can be stopped and restarted without losing progress, ensuring that previously processed domains are not crawled again within the same day.

6. **Continuous Writing and Graceful Interruption:**
   - Continuously writes progress to the JSON file after processing each domain. Handles graceful interruptions by saving the current state before exiting.

7. **Handling Duplicates:**
   - Ensures that duplicate emails are not added to the JSON file. Updates existing records only if new information is found.

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
```
urls
https://example.com
http://testsite.com
```

### `config.json`
```
{
    "scraping_settings": {
        "wait_time": 1,
        "timeout": 30000,
        "retry_attempts": 3
    },
    "search_keywords": {
        "contact_keywords": ["contact", "support", "help", "about", "info"]
    },
    "output_settings": {
        "enable_csv": false,
        "enable_schema_crawling": true
    },
    "api_keys": {
        "use_hunter": false,
        "hunter_api_key": "your_hunter_api_key_here"
    },
    "logging_settings": {
        "log_levels": {
            "DEBUG": true,
            "INFO": true,
            "WARNING": true,
            "ERROR": true
        }
    },
    "html_parsing": {
        "email_patterns": ["[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"]
    },
    "blacklisted_filetypes": ["jpg", "jpeg", "png", "gif", "bmp", "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "zip", "rar", "tar", "gz", "7z"]
}
```

### `example_output.json`
```
{
    "example.com": {
        "emails": [
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
        "organization": {
            "name": "Example Company",
            "url": "https://www.example.com",
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+1-800-555-5555",
                "contactType": "Customer Service"
            },
            "sameAs": [
                "https://www.facebook.com/example",
                "https://www.twitter.com/example",
                "https://www.linkedin.com/company/example"
            ]
        },
        "last_scraped": "2024-06-28"
    },
    "testsite.com": {
        "emails": [
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
        ],
        "organization": {
            "name": "Test Site",
            "url": "https://www.testsite.com",
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+1-800-555-5555",
                "contactType": "Customer Service"
            },
            "sameAs": [
                "https://www.facebook.com/testsite",
                "https://www.twitter.com/testsite",
                "https://www.linkedin.com/company/testsite"
            ]
        },
        "last_scraped": "2024-06-28"
    }
}
```

### `example_output.csv`
```
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