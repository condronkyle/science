import sqlite3
import os
from assistant import PaperScorer
api_key = os.getenv('OPENAI_API_KEY')

paper_scorer = PaperScorer(input_id='asst_vnANVGlFmmC1fRrl2I8JlxuI')

def create_thread():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": paper_scorer.instructions}
        ]
    )
    thread_id = response['id']
    return thread_id

def add_message_to_thread(thread_id, content):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        thread_id=thread_id,
        messages=[
            {"role": "user", "content": content}
        ]
    )
    return response['choices'][0]['message']['content']

def score_paper(thread_id):
    def get_novelty_score():
        message = "Please provide a novelty score for this paper."
        return add_message_to_thread(thread_id, message)

    def get_impact_score():
        message = "Please provide an impact score for this paper."
        return add_message_to_thread(thread_id, message)

    def get_validity_score():
        message = "Please provide a validity score for this paper."
        return add_message_to_thread(thread_id, message)

    def get_personal_score():
        message = "Please provide a personal score for this paper."
        return add_message_to_thread(thread_id, message)

    return {
        'novelty_score': get_novelty_score(),
        'impact_score': get_impact_score(),
        'validity_score': get_validity_score(),
        'personal_score': get_personal_score()
    }


def score_new_papers(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL to find papers not scored yet
    query = """
    SELECT paper_id, category FROM papers
    WHERE paper_id NOT IN (SELECT paper_id FROM scored_papers);
    """

    # Execute the query to find unscored papers
    cursor.execute(query)
    unscored_papers = cursor.fetchall()


    count = 1
    # Process each unscored paper
    for paper in unscored_papers:
        if count >5:
            exit
        paper_id = paper[0]
        category = paper[1]
        thread_id = create_thread()
        scores = score_paper(thread_id)

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

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f"Processed and scored {len(unscored_papers)} papers.")

# Path to your SQLite database
db_path = '/Users/kylecondron/Documents/coding/science/arxiv.db'

# Call the function to score unscored papers
score_new_papers(db_path)
