import urllib, urllib.parse, urllib.request

base_url = "http://export.arxiv.org/api/query"
params = {
    "search_query": 'all:electron',
    "sortBy": "submittedDate",
    "sortOrder": "descending",
    "maxResults": 1
}

# Encode the query parameters
encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

# Construct the full URL
url = f"{base_url}?{encoded_params}"

with urllib.request.urlopen(url) as results:
  r = results.read()
print(r)

data = urllib.request.urlopen(url).read()
print(data)

data = urllib.request.urlopen(url)
print(data.read().decode('utf-8'))


import urllib, urllib.request
url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1'
data = urllib.request.urlopen(url)
print(data.read().decode('utf-8'))