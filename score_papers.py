import sqlite3

import os
api_key = os.getenv('CHATGPT_API_KEY')


def score_paper():
    # Placeholder functions for scoring. Replace with actual scoring logic.
    def get_novel_score():
        return 5  # Placeholder value

    def get_exciting_score():
        return 6  # Placeholder value

    def get_validity_score():
        return 7  # Placeholder value

    def get_personal_score():
        return 8  # Placeholder value

    return {
        'novel_score': get_novel_score(),
        'exciting_score': get_exciting_score(),
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

    # Process each unscored paper
    for paper in unscored_papers:
        paper_id = paper[0]
        category = paper[1]
        scores = score_paper()

        # SQL to insert scored paper
        insert_sql = """
        INSERT INTO scored_papers (paper_id, novel_score, exciting_score, validity_score, personal_score, category)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor.execute(insert_sql, (
            paper_id,
            scores['novel_score'],
            scores['exciting_score'],
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
