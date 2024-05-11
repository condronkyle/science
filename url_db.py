import sqlite3
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# API call setup
base_url = "http://export.arxiv.org/api/query"
params = {
    "search_query": 'ti:"dark matter"',
    "sortBy": "lastUpdatedDate",
    "sortOrder": "descending",
    "max_results": 1
}
encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
url = f"{base_url}?{encoded_params}"

# Fetch data from the API
response = urllib.request.urlopen(url)
xml_data = response.read().decode('utf-8')

# Parse the XML data
root = ET.fromstring(xml_data)

# Connect to SQLite database (update the database path)
conn = sqlite3.connect('~/Documents/coding/arxiv/arxiv.db')
c = conn.cursor()

# SQL insert statement
insert_sql = '''
INSERT INTO papers (paper_name, summary, date_posted, category, link)
VALUES (?, ?, ?, ?, ?);
'''

# Process and insert data into the database
for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
    paper_name = entry.find('{http://www.w3.org/2005/Atom}title').text
    summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
    date_posted = entry.find('{http://www.w3.org/2005/Atom}published').text
    link = entry.find('{http://www.w3.org/2005/Atom}link[@rel="alternate"]').attrib['href']
    category = entry.find('{http://arxiv.org/schemas/atom}primary_category').attrib['term']

    # Execute the SQL command
    ##c.execute(insert_sql, (paper_name, summary, date_posted, category, link))
    print(insert_sql, (paper_name, summary, date_posted, category, link))


# Commit changes and close the connection
conn.commit()
conn.close()

print("Data successfully inserted into the database.")
