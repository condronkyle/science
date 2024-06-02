import urllib, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

base_url = "http://export.arxiv.org/api/query"
params = {
    "search_query": 'all:electron',
    "sortBy": "submittedDate",
    "sortOrder": "descending",
    "max_results": 1,
}

# Encode the query parameters
encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

# Construct the full URL
url = f"{base_url}?{encoded_params}"

# Fetch data from the API
response = urllib.request.urlopen(url)
xml_data = response.read().decode('utf-8')

print(xml_data)

# Parse the XML data
root = ET.fromstring(xml_data)
for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
    paper_name = entry.find('{http://www.w3.org/2005/Atom}title').text
    print(paper_name)