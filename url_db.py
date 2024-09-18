import sqlite3
import requests
from lxml import etree

# URL of the RSS feed
url = 'https://rss.arxiv.org/rss/astro-ph'

# Fetch data from the RSS feed with streaming
response = requests.get(url, stream=True)
response.raise_for_status()  # Check for request errors

# Connect to SQLite database (update the database path)
conn = sqlite3.connect('/Users/kylecondron/Documents/coding/science/arxiv.db')  # Update with your actual path
c = conn.cursor()

# SQL insert statement
insert_sql = '''
INSERT OR IGNORE INTO papers (paper_name, summary, date_posted, category, link)
VALUES (?, ?, ?, ?, ?);
'''

# Define namespaces (if any)
ns = {
    'arxiv': 'http://arxiv.org/schemas/atom',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'atom': 'http://www.w3.org/2005/Atom',
    'content': 'http://purl.org/rss/1.0/modules/content/',
}

# Use iterparse for efficient parsing
context = etree.iterparse(response.raw, events=('end',), tag='item')

for event, item in context:
    # Extract data from each <item> element
    paper_name_elem = item.find('title')
    paper_name = paper_name_elem.text.strip() if paper_name_elem is not None else None

    summary_elem = item.find('description')
    summary_raw = summary_elem.text.strip() if summary_elem is not None else None

    # Extract the abstract from the description
    # The description contains extra text before the abstract
    # We'll extract the text after 'Abstract:'
    summary = None
    if summary_raw:
        abstract_index = summary_raw.find('Abstract:')
        if abstract_index != -1:
            summary = summary_raw[abstract_index + len('Abstract:'):].strip()
        else:
            summary = summary_raw

    date_elem = item.find('pubDate')
    date_posted = date_elem.text.strip() if date_elem is not None else None

    link_elem = item.find('link')
    link = link_elem.text.strip() if link_elem is not None else None

    category_elems = item.findall('category')
    categories = [elem.text.strip() for elem in category_elems if elem.text]
    category = ', '.join(categories) if categories else None

    # Execute the SQL command
    c.execute(insert_sql, (paper_name, summary, date_posted, category, link))

    # Clear the element from memory
    item.clear()
    while item.getprevious() is not None:
        del item.getparent()[0]

# Clean up the parser
del context

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data successfully inserted into the database.")
