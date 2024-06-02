import feedparser

# URL of the RSS feed
rss_url = 'http://example.com/rss/cs'

def fetch_rss_feed(url):
    feed = feedparser.parse(url)
    for entry in feed.entries:
        print(f"Title: {entry.title}")
        print(f"Link: {entry.link}")
        print(f"Published: {entry.published}")
        print(f"Summary: {entry.summary}")
        print()

if __name__ == "__main__":
    fetch_rss_feed(rss_url)
