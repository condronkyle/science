import sqlite3
import requests
from lxml import etree
import urllib.parse

url = "https://rss.arxiv.org/rss/astro-ph"

# Fetch data from the API with streaming
response = requests.get(url, stream=True)
response.raise_for_status()  # Check for request errors


# Check the response content
print("Status Code:", response.status_code)
print("Content-Type:", response.headers.get('Content-Type'))

# After fetching the response
response.raise_for_status()  # Check for request errors
response.raw.decode_content = True  # Ensure content is decoded

# Connect to SQLite database (update the database path)
conn = sqlite3.connect('/Users/kylecondron/Documents/coding/science/arxiv.db')
c = conn.cursor()

# SQL insert statement
insert_sql = '''
INSERT INTO papers (paper_name, summary, date_posted, category, link)
VALUES (?, ?, ?, ?, ?);
'''

# Define namespaces
ns = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}

# Use iterparse for efficient parsing
context = etree.iterparse(response.raw, events=('end',), tag='{http://www.w3.org/2005/Atom}entry')

for event, elem in context:
    # Extract data from each <entry> element
    paper_name = elem.find('atom:title', namespaces=ns).text.strip()
    summary = elem.find('atom:summary', namespaces=ns).text.strip()
    date_posted = elem.find('atom:published', namespaces=ns).text.strip()
    link_elem = elem.find('atom:link[@rel="alternate"]', namespaces=ns)
    link = link_elem.get('href') if link_elem is not None else None
    primary_category_elem = elem.find('arxiv:primary_category', namespaces=ns)
    category = primary_category_elem.get('term') if primary_category_elem is not None else None

    # Execute the SQL command
    c.execute(insert_sql, (paper_name, summary, date_posted, category, link))

    # Clear the element from memory to free up resources
    elem.clear()
    while elem.getprevious() is not None:
        del elem.getparent()[0]

# Clean up the parser
del context

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data successfully inserted into the database.")
