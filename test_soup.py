import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from openai import OpenAI

# Set environment variables for testing
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
os.environ["condronkbucket"] = "your_s3_bucket_name_here"

def process_rss_feed():
    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    assistant_id = "asst_i4LBbl5pzLCQsTB3WsUiczmX"

    # Define the RSS feed URL
    feed_url = "https://rss.arxiv.org/rss/math"

    # Fetch and parse the RSS feed
    response = requests.get(feed_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch RSS feed: {response.status_code}")
    soup = BeautifulSoup(response.content, "xml")

    # Prepare results
    results = []

    # Process each paper in the feed
    for item in soup.find_all("item"):
        title = item.title.text
        abstract = item.description.text

        print(f"Processing: {title}\nAbstract: {abstract}\n")

        # Create a new Thread
        thread = client.beta.threads.create()

        # Add a user message
        user_msg = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Title: {title}\nAbstract: {abstract}"
        )

        # Run the assistant
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # Get the assistant's response
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            response = messages.data[0].content[0].text.value.strip()
        else:
            response = f"Error: Run did not complete. Status: {run.status}"

        print(f"Response: {response}\n")

        # Store the result
        results.append({
            "title": title,
            "response": response
        })

    # Save results locally
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_file = f"arxiv_math_results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Processed {len(results)} papers. Results saved to {output_file}")

if __name__ == "__main__":
    process_rss_feed()