"""
Test script to parse a saved Bisnow email and extract articles.
Save a .eml file from Gmail and run this to test article extraction.
"""

import email
from bs4 import BeautifulSoup
import sys

def extract_articles_from_eml(eml_path):
    """Extract articles from a saved .eml file."""
    with open(eml_path, 'r', encoding='utf-8') as f:
        msg = email.message_from_file(f)

    # Get subject
    subject = msg.get('Subject', '')
    sender = msg.get('From', '')

    print(f"Subject: {subject}")
    print(f"From: {sender}")
    print("=" * 80)

    # Get HTML content
    html_content = None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
    else:
        if msg.get_content_type() == 'text/html':
            html_content = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

    if not html_content:
        print("No HTML content found!")
        return

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all links
    print("\nAll links in email:")
    print("-" * 80)
    all_links = soup.find_all('a', href=True)
    for i, link in enumerate(all_links, 1):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if 'bisnow.com' in href and '/news/' in href:
            print(f"{i}. [{text}] -> {href[:80]}...")

    # Find all bold/strong tags
    print("\n\nAll bold/strong text:")
    print("-" * 80)
    bold_tags = soup.find_all(['strong', 'b'])
    for i, tag in enumerate(bold_tags, 1):
        text = tag.get_text(strip=True)
        if len(text) > 10 and len(text) < 200:
            print(f"{i}. {text}")

    # Find all headings
    print("\n\nAll headings (h1-h6):")
    print("-" * 80)
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for i, tag in enumerate(headings, 1):
        text = tag.get_text(strip=True)
        print(f"{i}. [{tag.name}] {text}")

    # Find paragraphs with strong styling or large font
    print("\n\nParagraphs with inline styles (potential headlines):")
    print("-" * 80)
    paragraphs = soup.find_all('p')
    for i, p in enumerate(paragraphs[:20], 1):  # First 20 paragraphs
        style = p.get('style', '')
        text = p.get_text(strip=True)
        if ('font-weight' in style or 'font-size' in style) and len(text) > 10 and len(text) < 200:
            print(f"{i}. {text[:100]}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_email_parsing.py <path_to_eml_file>")
        print("\nTo save an email as .eml:")
        print("1. Open the email in Gmail")
        print("2. Click the three dots > Download message")
        print("3. Save the .eml file")
        sys.exit(1)

    extract_articles_from_eml(sys.argv[1])
