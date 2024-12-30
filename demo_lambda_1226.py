import os
import json
import boto3
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from openai import OpenAI

def lambda_handler(event, context):

    # 1) Instantiate the OpenAI client
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    assistant_id = "asst_O0SoiP3rRHetL8SSTUJE7B3s"

    """
    AWS Lambda function that:
      1) Reads today's arXiv math RSS feed
      2) For each paper, creates a new Thread, adds a user message, and runs the Assistant
      3) Stores the results in S3 as a JSON file
    """


    # 3) Define the RSS feed URL (arXiv Math in this example)
    feed_url = "https://rss.arxiv.org/rss/math"

    # Fetch and parse the RSS feed
    response = requests.get(feed_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch RSS feed: {response.status_code}")
    soup = BeautifulSoup(response.content, "xml")

    # Prepare results
    results = []

    # Process each paper in the feed
    # for item in soup.find_all("item"):
    for item in ["a","b"]:
        # title = item.title.text
        # abstract = item.description.text

        print(f"Processing: {title}\nAbstract: {abstract}\n")

        # 5) Create a new Thread for each paper
        thread = client.beta.threads.create()

        # 6) Add a user message
        user_content = f"test just saying hi"
        user_msg = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_content
        )

        # 7) Create (and poll) a Run on this Thread with our Assistant
        #    This is the actual "model invocation" that will produce an assistant message in the Thread
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # 8) Once run completes, retrieve the new messages (the assistant's response)
        if run.status == "completed":
            # We can list the messages in the thread
            messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
            response = messages.data[0].content[0].text.value
            print(response.strip())
        else:
            classification = f"Error: Run did not complete. Status: {run.status}"

        # 9) Store the result in memory
        results.append({
            "scores": classification
        })

        # 10) Write results to S3 as a JSON
        s3 = boto3.client("s3")
        bucket_name = os.environ["condronkbucket"]
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        s3_key = f"arxiv_math_scores_{timestamp}.json"

        body_json = json.dumps(results, indent=2)

        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=body_json
        )

        return {
            "statusCode": 200,
            "body": f"Processed {len(results)} papers. Results in s3://{bucket_name}/{s3_key}"
        }