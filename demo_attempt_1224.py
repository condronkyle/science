import feedparser
import openai
from openai import OpenAI
import os

# 1) Instantiate the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 2) Define the RSS feed URL
feed_url = "https://rss.arxiv.org/rss/nlin"

# 3) Parse the feed
feed = feedparser.parse(feed_url)

# 4) System message to guide the model's output
SYSTEM_PROMPT = """
You are an expert paper reviewer assessing thousands of research papers across diverse disciplines.
You will be provided with a paper's title (and optionally its abstract).
Assign three separate scores on a scale of 1–10:
1. Novelty
2. Impact
3. Validity

When given paper info, output ONLY the following in valid JSON with keys: "novelty", "impact", and "validity".
For example:
{
  "novelty": 3,
  "impact": 1,
  "validity": 2
}

Please be incredibly discerning, in past testing you generally assign very similar scores to each paper.
Trust your instincts, if a paper seems weak, assign very low. If it seems intriguing, assign very high.
"""

# 5) Loop over each entry in the RSS feed
for entry in feed.entries[0:1]:
    title = entry.title
    abstract = entry.summary
    print(abstract)

    # Optional: some feeds have 'summary' for the abstract, but it might include HTML tags
    # abstract = entry.summary

    # 6) Create the chat messages
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""Title: {title}, Abstract: {abstract}"""
        }
    ]

    # 7) Call the new Chat Completions API
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4", depending on your plan
            messages=messages,
            temperature=0.8,
            max_tokens=50
        )

        # 8) Extract the response content
        # (the model’s text is in completion.choices[0].message["content"])
        scores_json = completion.choices[0].message

        # 9) Print or log the results
        print(f"Title: {title}")
        print(f"Abstract: {abstract}")
        print(f"Scores: {scores_json}")
        print("-" * 60)

    except Exception as e:
        print(f"Error processing paper '{title}': {e}")