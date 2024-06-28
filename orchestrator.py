import csv
import json
import os
import sys
import time
from datetime import datetime
from urllib.parse import urlparse
import requests
from playwright.sync_api import sync_playwright
import argparse
import logging
from web_extractor import scrape_page, is_valid_email

def load_config(config_path="config.json"):
    with open(config_path, "r") as file:
        return json.load(file)

def check_and_add_header(input_csv):
    with open(input_csv, 'r') as file:
        first_line = file.readline().strip()
        if 'urls' not in first_line:
            lines = file.readlines()
            with open(input_csv, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['urls'])
                for line in lines:
                    writer.writerow([line.strip()])

def load_urls(input_csv):
    with open(input_csv, "r") as file:
        reader = csv.DictReader(file)
        return [row['urls'] for row in reader]

def load_existing_json(output_json_file):
    if os.path.exists(output_json_file):
        try:
            with open(output_json_file, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            logging.error(f"Error reading {output_json_file}, it seems to be corrupted. Overwriting the file.")
    return {}

def save_json(data, output_file):
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)

def save_csv(data, output_file):
    with open(output_file, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["domain", "email", "first_name", "last_name", "position", "confidence"])
        for domain, info in data.items():
            for email in info['emails']:
                writer.writerow([domain, email["value"], email.get("first_name"), email.get("last_name"), email.get("position"), email.get("confidence")])

def enrich_with_hunter(domain, config):
    if not config["api_keys"]["use_hunter"]:
        return []
    api_key = config["api_keys"]["hunter_api_key"]
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        emails = data.get('data', {}).get('emails', [])
        for email in emails:
            email.pop('sources', None)
        return emails
    except Exception as e:
        logging.error(f"Error using Hunter API for {domain}: {e}")
        return []

def setup_logging(config):
    today = datetime.today().strftime('%Y-%m-%d')
    log_file = f"email-scrape-log-{today}.log"
    log_levels = config["logging_settings"]["log_levels"]

    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG if log_levels["DEBUG"] else (logging.INFO if log_levels["INFO"] else (logging.WARNING if log_levels["WARNING"] else logging.ERROR)),
        format='%(asctime)s - %(levelname)s - %(message)s',  # Corrected line
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if log_levels["DEBUG"] else (logging.INFO if log_levels["INFO"] else (logging.WARNING if log_levels["WARNING"] else logging.ERROR)))
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')  # Corrected line
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def ensure_schema(url):
    if not urlparse(url).scheme:
        return 'https://' + url
    return url

def scrape_with_fallback(url, browser, blacklisted_filetypes, enable_schema_crawling, contact_keywords, email_patterns, timeout, retry_attempts):
    attempts = 0
    while attempts < retry_attempts:
        try:
            return scrape_page(url, browser, blacklisted_filetypes, enable_schema_crawling, contact_keywords, email_patterns, timeout)
        except Exception as e:
            logging.error(f"Error scraping {url} on attempt {attempts + 1}: {e}")
            attempts += 1
            if attempts >= retry_attempts:
                logging.error(f"Failed to scrape {url} after {retry_attempts} attempts.")
                return [], {}

def should_skip_domain(domain, existing_data):
    today_str = datetime.today().strftime('%Y-%m-%d')
    return domain in existing_data and existing_data[domain].get('last_scraped') == today_str

def update_json_data(existing_data, domain, emails, org_info):
    today_str = datetime.today().strftime('%Y-%m-%d')
    if domain not in existing_data:
        existing_data[domain] = {"emails": [], "organization": {}, "last_scraped": today_str}

    existing_emails = {email['value'] for email in existing_data[domain]['emails']}
    new_emails = [email for email in emails if email['value'] not in existing_emails]
    existing_data[domain]['emails'].extend(new_emails)

    if org_info:
        existing_data[domain]['organization'] = org_info

    existing_data[domain]['last_scraped'] = today_str

def convert_json_to_csv(json_file, output_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    save_csv(data, output_file)
    logging.info(f"Converted {json_file} to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Email scraper script.")
    parser.add_argument("input_file", help="Input CSV file with URLs or JSON file for conversion.")
    parser.add_argument("-o", "--output_format", choices=["json", "csv"], default="json", help="Output format: json or csv.")
    parser.add_argument("-convert", action="store_true", help="Convert JSON file to CSV format.")
    args = parser.parse_args()

    config = load_config()
    setup_logging(config)

    if args.convert:
        if not args.input_file.endswith(".json"):
            logging.error("Input file for conversion must be a JSON file.")
            sys.exit(1)
        output_csv_file = args.input_file.replace(".json", ".csv")
        convert_json_to_csv(args.input_file, output_csv_file)
        sys.exit(0)

    check_and_add_header(args.input_file)
    urls = load_urls(args.input_file)
    today = datetime.today().strftime('%Y-%m-%d')
    output_json_file = f"email-scrape-{today}.json"
    
    existing_data = load_existing_json(output_json_file)
    total_urls = len(urls)
    logging.info(f"Starting email scraping for {total_urls} domains.")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
            for idx, url in enumerate(urls, 1):
                url = ensure_schema(url)
                logging.info(f"Processing {idx}/{total_urls}: {url}")
                domain = urlparse(url).netloc
                if not domain:
                    logging.error(f"Invalid URL: {url}")
                    continue

                if should_skip_domain(domain, existing_data):
                    logging.info(f"Skipping {domain} as it has already been scraped today.")
                    continue
                
                emails, org_info = scrape_with_fallback(
                    url, browser, config["blacklisted_filetypes"],
                    config["output_settings"]["enable_schema_crawling"],
                    config["search_keywords"]["contact_keywords"],
                    config["html_parsing"]["email_patterns"],
                    config["scraping_settings"]["timeout"],
                    config["scraping_settings"]["retry_attempts"]
                )
                if config["api_keys"]["use_hunter"]:
                    hunter_emails = enrich_with_hunter(domain, config)
                    emails.extend(hunter_emails)
                
                update_json_data(existing_data, domain, emails, org_info)
                email_values = [email['value'] for email in emails if 'value' in email]
                if email_values:
                    logging.info(f"Found emails for {domain}: {', '.join(email_values)}")
                else:
                    logging.info(f"No emails found for {domain}")

                save_json(existing_data, output_json_file)  # Save after each domain

                time.sleep(config["scraping_settings"]["wait_time"])
                logging.info(f"Completed {idx}/{total_urls} domains.")
            
            browser.close()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        save_json(existing_data, output_json_file)  # Save before exiting in case of error
    finally:
        save_json(existing_data, output_json_file)
        logging.info(f"Output saved to {output_json_file}")
        
        if args.output_format == "csv" or config["output_settings"]["enable_csv"]:
            output_csv_file = output_json_file.replace(".json", ".csv")
            save_csv(existing_data, output_csv_file)
            logging.info(f"Output saved to {output_csv_file}")

if __name__ == "__main__":
    main()