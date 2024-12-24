import sqlite3
import os
import time
from openai import OpenAI, AssistantEventHandler
from assistant import PaperScorer
from typing_extensions import override
import json

api_key=os.environ.get("OPENAI_API_KEY")

paper_scorer = PaperScorer("asst_J8DdlZtrejFTHrJqsnm6aDM9")

client = OpenAI(
    # This is the default and can be omitted
    api_key=api_key,
    organization="org-mk6aNQLOgm5XgkiiEfNzFduz"
)


def add_message_to_thread(thread_id, message):

    new_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=paper_scorer.assistant_id,
    )
    while True:
        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=thread_id
            )
            response = messages.data[0].content[0].text.value
            break
        else:
            print(run.status)
            time.sleep(5)
    return response

def get_novelty_score(thread_id):
    message = "Please provide a novelty score for this paper."
    return add_message_to_thread(thread_id, message)

def get_impact_score(thread_id):
    message = "Please provide an impact score for this paper."
    return add_message_to_thread(thread_id, message)

def get_validity_score(thread_id):
    message = "Please provide a validity score for this paper."
    return add_message_to_thread(thread_id, message)

def get_personal_score(thread_id):
    return 5
    # message = "Please provide a personal score for this paper."
    # return add_message_to_thread(thread_id, message)

def score_paper(title, abstract):
    thread = client.beta.threads.create()
    thread_id = thread.id

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"""Paper Title: {title}
        Paper Abstract: {abstract}
        """
    )

    return {
        'novelty_score': get_novelty_score(thread_id),
        'impact_score': get_impact_score(thread_id),
        'validity_score': get_validity_score(thread_id),
        'personal_score': get_personal_score(thread_id)
    }


def score_new_papers(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL to find papers not scored yet
    query = """
    SELECT paper_id, category, paper_name, summary FROM papers
    WHERE paper_id NOT IN (SELECT paper_id FROM scored_papers);
    """

    # Execute the query to find unscored papers
    cursor.execute(query)
    unscored_papers = cursor.fetchall()


    count = 1
    # Process each unscored paper
    for paper in unscored_papers:
        if count > 20:
            exit()
        count=count+1
        paper_id = paper[0]
        category = paper[1]
        title = paper[2]
        abstract = paper[3]
        print(title)
        scores = score_paper(title, abstract)

        print(str(paper_id) + "\n" + category + "\n" + title + "\n" + str(scores))

        # SQL to insert scored paper
        insert_sql = """
        INSERT INTO scored_papers (paper_id, novelty_score, impact_score, validity_score, personal_score, category)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor.execute(insert_sql, (
            paper_id,
            scores['novelty_score'],
            scores['impact_score'],
            scores['validity_score'],
            scores['personal_score'],
            category
        ))
        conn.commit()
        print("sql executed")

    print(f"Processed and scored {len(unscored_papers)} papers.")
    # Commit changes and close the connection
    conn.close()

# Path to your SQLite database
db_path = '/Users/kylecondron/Documents/coding/science/arxiv.db'

# Call the function to score unscored papers
score_new_papers(db_path)
