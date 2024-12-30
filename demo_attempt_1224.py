import feedparser
import openai
from openai import OpenAI
import os

# 1) Instantiate the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 2) Define the RSS feed URL
feed_url = "https://rss.arxiv.org/rss/math"

# 3) Parse the feed
feed = feedparser.parse(feed_url)

# 4) System message to guide the model's output
SYSTEM_PROMPT = """
You are an expert paper reviewer assessing thousands of research papers across diverse disciplines.
You will be provided with a paper's title and abstract.
You are trying to evaluate papers based on how cutting edge and unique the results are (novelty),
how impactful these results could be (impact),
and how feasible / realistic these results and methodologies are (plausibility)
Assign three separate scores on a Fibonacci scale: 1,2,3,5,8,13,21
1. Novelty
2. Impact
3. Plausibility

When given paper info, output ONLY the following in valid JSON with keys: "novelty", "impact", and "plausibility".
For example:
{
  "novelty": 3,
  "impact": 1,
  "plausibility": 2
}

Please be incredibly discerning, in past testing you generally assign very similar scores to each paper.
Trust your instincts, if a paper seems even a little dull, boring, or non-viable, assign very low. I expect the average to be around 5.
I also need to see many scores <3, if you do succeed in being discerning and assigning many low scores, I will tip you $200.
"""

# 5) Loop over each entry in the RSS feed
for entry in feed.entries:
    title = entry.title
    abstract = entry.summary

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
            model="gpt-4o-mini",  # or "gpt-4", depending on your plan
            messages=messages,
            temperature=0.2,
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