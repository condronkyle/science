import os
from openai import OpenAI

# 1) Instantiate the OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# 2) Create the Assistant (Beta)
#    This is where you put your system instructions, model, etc.
#    "tools" is empty here, but you could enable code interpreter or file search if needed.
assistant = client.beta.assistants.create(
    name="Paper Reviewer",
    instructions="""
You are an expert paper reviewer assessing thousands of research papers across diverse disciplines.
Assign three separate scores on a Fibonacci scale (1,2,3,5,8,13,21) for:
1. Novelty
2. Impact
3. Validity

Be very discerning. If a paper seems dull, assign a very low score. We expect an average around 5.
Many scores less than 3 would be great.

Output ONLY valid JSON with keys: "novelty", "impact", and "validity", exactly like this:
{
  "novelty": 1,
  "impact": 1,
  "validity": 1
}.
""",
    tools=[],  # no tools in this example
    model="gpt-4o-mini"  # or "gpt-4", "gpt-3.5-turbo", etc.
)

print(assistant)