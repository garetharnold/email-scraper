import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging
import json

def find_emails(text, email_patterns):
    emails = set()
    for pattern in email_patterns:
        emails.update(re.findall(pattern, text))
    return emails

def is_valid_email(email, blacklisted_filetypes):
    domain = email.split('@')[-1]
    extension = domain.split('.')[-1].lower()
    return extension not in blacklisted_filetypes

def parse_organization_schema(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    org_info = {}
    schema_tags = soup.find_all('script', type='application/ld+json')
    for tag in schema_tags:
        try:
            schema = json.loads(tag.string)
            if schema.get('@type') == 'Organization':
                org_info = schema  # Extract all information from the organization schema
                break
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
    return org_info

def find_contact_links(html, keywords):
    soup = BeautifulSoup(html, 'html.parser')
    contact_links = set()
    for keyword in keywords:
        contact_links.update(soup.find_all('a', href=True, text=re.compile(keyword, re.IGNORECASE)))
        contact_links.update(soup.find_all('a', href=re.compile(keyword, re.IGNORECASE)))
    return contact_links

def scrape_page(url, browser, blacklisted_filetypes, enable_schema_crawling, contact_keywords, email_patterns, timeout):
    try:
        page = browser.new_page()
        page.set_default_timeout(timeout)
        page.goto(url)
        content = page.content()
        html_source = page.evaluate("() => document.documentElement.outerHTML")

        # Find emails in both HTML source and rendered content
        emails = find_emails(content, email_patterns) | find_emails(html_source, email_patterns)

        # Check for links with the word "contact" in the text or URL in rendered content
        for keyword in contact_keywords:
            contact_links = page.locator(f'a:has-text("{keyword}")').all() + page.locator(f'a[href*="{keyword}"]').all()
            for contact_link in contact_links:
                contact_url = contact_link.get_attribute('href')
                if contact_url:
                    if contact_url.startswith('mailto:'):
                        email = contact_url[len('mailto:'):]
                        logging.info(f"Found email link: {email}")
                        emails.add(email)
                    else:
                        if not urlparse(contact_url).scheme:
                            contact_url = urljoin(url, contact_url)
                        page.goto(contact_url)
                        emails.update(find_emails(page.content(), email_patterns))

        # Check for links with the word "contact" in the text or URL in HTML source
        source_contact_links = find_contact_links(html_source, contact_keywords)
        for contact_link in source_contact_links:
            contact_url = contact_link['href']
            if contact_url.startswith('mailto:'):
                email = contact_url[len('mailto:'):]
                logging.info(f"Found email link: {email}")
                emails.add(email)
            else:
                if not urlparse(contact_url).scheme:
                    contact_url = urljoin(url, contact_url)
                page.goto(contact_url)
                emails.update(find_emails(page.content(), email_patterns))

        # Parse organization schema information if enabled
        org_info = parse_organization_schema(html_source) if enable_schema_crawling else {}

        page.close()
        valid_emails = [{"value": email if not email.startswith('mailto:') else email[len('mailto:'):] for email in emails if is_valid_email(email, blacklisted_filetypes)}]
        return valid_emails, org_info
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return [], {}