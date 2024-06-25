import sqlite3
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_rss_data(url, retries=3, sleep_time=2):
    attempts = 0
    while attempts < retries:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Will raise an HTTPError for bad responses
            return response.text
        except requests.exceptions.RequestException as e:
            attempts += 1
            print(f"Attempt {attempts} failed: {e}")
            if attempts >= retries:
                raise Exception("Failed to fetch complete RSS data after several retries.")
            time.sleep(sleep_time)

def escape_special_characters(xml_data):
    # Replace backslashes with double backslashes
    xml_data = xml_data.replace("\\", "\\\\")
    return xml_data

# RSS feed URL
rss_url = "http://rss.arxiv.org/rss/astro-ph"

# Attempt to fetch and parse the data
xml_data = fetch_rss_data(rss_url)

# Log fetched data to file for inspection
with open('fetched_rss_data.xml', 'w', encoding='utf-8') as file:
    file.write(xml_data)

# Print the length of the fetched XML data for inspection
print(f"Fetched XML data length: {len(xml_data)}")

# Escape special characters before parsing
xml_data = escape_special_characters(xml_data)

# Parse the XML data
try:
    root = ET.fromstring(xml_data)
except ET.ParseError as e:
    print(f"Error parsing XML data: {e}")
    # Log the problematic part of the XML data
    lines = xml_data.splitlines()
    for i, line in enumerate(lines):
        print(f"Line {i+1}: {line}")
    exit(1)

# Connect to SQLite database (update the database path)
conn = sqlite3.connect('/Users/kylecondron/Documents/coding/science/arxiv.db')
c = conn.cursor()

# SQL insert statement with ON CONFLICT clause to ignore duplicates
insert_sql = '''
INSERT OR IGNORE INTO papers (paper_name, summary, date_posted, category, link)
VALUES (?, ?, ?, ?, ?);
'''

# Process and insert data into the database
for item in root.findall('.//item'):
    announce_type = item.find('{http://arxiv.org/schemas/atom}announce_type')
    if announce_type is not None and announce_type.text == 'new':
        paper_name = item.find('title').text if item.find('title') is not None else None
        description = item.find('description').text if item.find('description') is not None else None
        # Extract abstract from description
        if description and "Abstract:" in description:
            description = description.split("Abstract:", 1)[1].strip()
        else:
            description = None
        date_posted = datetime.today().strftime('%Y-%m-%d')
        link = item.find('link').text if item.find('link') is not None else None
        categories = [category.text for category in item.findall('category')]
        category = ', '.join(categories) if categories else None

        # Execute the SQL command if link is not None
        if link is not None:
            c.execute(insert_sql, (paper_name, description, date_posted, category, link))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data successfully inserted into the database.")
