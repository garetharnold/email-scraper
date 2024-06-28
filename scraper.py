import csv
import json
import os
import sys
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin

import requests
from playwright.sync_api import sync_playwright
import argparse
import logging

# List of common file extensions to be excluded
BLACKLISTED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'tar', 'gz', '7z']

def load_config(config_path="config.json"):
    with open(config_path, "r") as file:
        return json.load(file)

def check_and_add_header(input_csv):
    with open(input_csv, 'r') as file:
        first_line = file.readline().strip()
        if 'urls' not in first_line:
            lines = file.readlines()
            with open(input_csv, 'w', newline='') as write_file:
                writer = csv.writer(write_file)
                writer.writerow(['urls'])
                for line in lines:
                    writer.writerow([line.strip()])

def load_urls(input_csv):
    with open(input_csv, "r") as file:
        reader = csv.DictReader(file)
        return [row['urls'] for row in reader]

def save_json(data, output_file):
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)

def save_csv(data, output_file):
    with open(output_file, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["domain", "email", "first_name", "last_name", "position", "confidence"])
        for domain, emails in data.items():
            for email in emails:
                writer.writerow([domain, email["value"], email.get("first_name"), email.get("last_name"), email.get("position"), email.get("confidence")])

def find_emails(page_content):
    emails = set()
    import re
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, page_content)
    emails.update(matches)
    return emails

def is_valid_email(email):
    domain = email.split('@')[-1]
    extension = domain.split('.')[-1].lower()
    return extension not in BLACKLISTED_EXTENSIONS

def scrape_page(url, browser):
    try:
        page = browser.new_page()
        page.goto(url)
        content = page.content()
        emails = find_emails(content)
        contact_page = page.locator('a:has-text("contact")').first
        if contact_page:
            contact_url = contact_page.get_attribute('href')
            if contact_url:
                if contact_url.startswith('mailto:'):
                    email = contact_url[len('mailto:'):]
                    logging.info(f"Found email link: {email}")
                    emails.add(email)
                else:
                    if not urlparse(contact_url).scheme:
                        contact_url = urljoin(url, contact_url)
                    page.goto(contact_url)
                    emails.update(find_emails(page.content()))
        page.close()
        return [{"value": email if not email.startswith('mailto:') else email[len('mailto:'):] for email in emails if is_valid_email(email)}]
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return []

def enrich_with_hunter(domain, config):
    api_key = config.get("api_key")
    if not api_key:
        return []
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        emails = data.get('data', {}).get('emails', [])
        # Remove sources information from emails
        for email in emails:
            email.pop('sources', None)
        return emails
    except Exception as e:
        logging.error(f"Error using Hunter API for {domain}: {e}")
        return []

def setup_logging():
    log_file = f"email-scrape-log-{datetime.today().strftime('%Y-%m-%d')}.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def ensure_schema(url):
    if not urlparse(url).scheme:
        return 'https://' + url
    return url

def scrape_with_fallback(url, browser):
    try:
        return scrape_page(url, browser)
    except Exception as e:
        logging.error(f"Error with HTTPS: {e}, trying HTTP...")
        http_url = 'http://' + urlparse(url).netloc
        return scrape_page(http_url, browser)

def convert_json_to_csv(json_file, output_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    save_csv(data, output_file)
    logging.info(f"Converted {json_file} to {output_file}")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Email scraper script.")
    parser.add_argument("input_file", help="Input CSV file with URLs or JSON file for conversion.")
    parser.add_argument("-o", "--output_format", choices=["json", "csv"], default="json", help="Output format: json or csv.")
    parser.add_argument("-convert", action="store_true", help="Convert JSON file to CSV format.")
    args = parser.parse_args()

    if args.convert:
        if not args.input_file.endswith(".json"):
            logging.error("Input file for conversion must be a JSON file.")
            sys.exit(1)
        output_csv_file = args.input_file.replace(".json", ".csv")
        convert_json_to_csv(args.input_file, output_csv_file)
        sys.exit(0)

    config = load_config()
    check_and_add_header(args.input_file)
    urls = load_urls(args.input_file)
    result = {}
    output_json_file = f"email-scrape-{datetime.today().strftime('%Y-%m-%d')}.json"
    
    total_urls = len(urls)
    logging.info(f"Starting email scraping for {total_urls} domains.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for idx, url in enumerate(urls, 1):
            url = ensure_schema(url)
            logging.info(f"Processing {idx}/{total_urls}: {url}")
            domain = urlparse(url).netloc
            if not domain:
                logging.error(f"Invalid URL: {url}")
                continue
            
            emails = scrape_with_fallback(url, browser)
            if config.get("use_hunter", False):
                hunter_emails = enrich_with_hunter(domain, config)
                emails.extend(hunter_emails)
            
            if emails:
                if domain not in result:
                    result[domain] = []
                result[domain].extend(emails)
                email_values = [email['value'] for email in emails if 'value' in email]
                if email_values:
                    logging.info(f"Found emails for {domain}: {', '.join(email_values)}")
                else:
                    logging.info(f"No emails found for {domain}")
            
            time.sleep(config.get("wait_time", 1))
            logging.info(f"Completed {idx}/{total_urls} domains.")
        
        browser.close()
    
    save_json(result, output_json_file)
    logging.info(f"Output saved to {output_json_file}")
    
    if args.output_format == "csv":
        output_csv_file = output_json_file.replace(".json", ".csv")
        save_csv(result, output_csv_file)
        logging.info(f"Output saved to {output_csv_file}")

if __name__ == "__main__":
    main()