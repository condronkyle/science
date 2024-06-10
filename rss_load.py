import sqlite3
import urllib.request
import xml.etree.ElementTree as ET
import http.client

# Function to fetch RSS data with retry mechanism
def fetch_rss_data(url):
    try:
        response = urllib.request.urlopen(url)
        return response.read().decode('utf-8')
    except http.client.IncompleteRead as e:
        return e.partial.decode('utf-8')

# RSS feed URL
rss_url = "http://rss.arxiv.org/rss/cs+q-bio+astro-ph+cond-mat+econ+eess+gr-qc+hep-lat+hep-ph+hep-th+math+nlin+nucl-ex+nucl-th+physics+q-bio+q-fin+quant-ph+stat"

# Fetch data from the RSS feed
xml_data = fetch_rss_data(rss_url)

# Parse the XML data
root = ET.fromstring(xml_data)

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
    paper_name = item.find('title').text
    summary = item.find('description').text
    date_posted = item.find('pubDate').text
    link = item.find('link').text
    categories = [category.text for category in item.findall('category')]
    category = ', '.join(categories) if categories else None

    # Execute the SQL command
    c.execute(insert_sql, (paper_name, summary, date_posted, category, link))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data successfully inserted into the database.")
