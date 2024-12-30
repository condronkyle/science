import os
import json
import boto3
from datetime import datetime
from openai import OpenAI
import logging
import time

# Set up logging immediately
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Log that we've started imports
print("Starting imports...")
logger.debug("Starting imports...")

def get_secret(secret_name):
    print(f"Attempting to get secret: {secret_name}")
    try:
        client = boto3.client('secretsmanager')
        print("Created secretsmanager client")
        response = client.get_secret_value(SecretId=secret_name)
        print("Got secret value")
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Error in get_secret: {str(e)}")
        raise

def lambda_handler(event, context):

    # 1) Instantiate the OpenAI client
    secret = get_secret('openai_apikey')
    api_key = secret['openai_apikey']
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    assistant_id = "asst_O0SoiP3rRHetL8SSTUJE7B3s"


    # 2) Define the RSS feed URL (arXiv Math in this example)
    feed_url = "https://rss.arxiv.org/rss/math"

    # 3) Parse the feed
    feed = feedparser.parse(feed_url)

    # We'll store results in a list, then write one JSON file to S3
    results = []

    # for entry in feed.entries: TODO replace with rss tmrw
    for entry in ["a","b"]:
        # TODO uncomment
        # title = entry.title
        # abstract = entry.summary

        # 4) Create a new Thread for each paper
        thread = client.beta.threads.create()

        # 5) Add a user message
        user_content = f"test just saying hi"
        user_msg = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_content
        )

        # 6) Create (and poll) a Run on this Thread with our Assistant
        #    This is the actual "model invocation" that will produce an assistant message in the Thread
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # 7) Once run completes, retrieve the new messages (the assistant's response)
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