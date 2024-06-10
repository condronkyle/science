import sqlite3


def create_tables(db_path):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL to create the 'papers' table
    create_papers_sql = """
    CREATE TABLE IF NOT EXISTS papers (
        paper_id INTEGER PRIMARY KEY AUTOINCREMENT,
        paper_name TEXT NOT NULL,
        summary TEXT,
        date_posted TEXT,
        category TEXT,
        link TEXT UNIQUE,
        source TEXT
    );
    """

    # SQL to create the 'scored_papers' table
    create_scored_papers_sql = """
    CREATE TABLE IF NOT EXISTS scored_papers (
        paper_id INTEGER PRIMARY KEY,
        novel_score INTEGER,
        exciting_score INTEGER,
        validity_score INTEGER,
        personal_score INTEGER,
        category TEXT
    );
    """

    # Execute the create table SQL for 'papers'
    cursor.execute(create_papers_sql)
    # Execute the create table SQL for 'scored_papers'
    cursor.execute(create_scored_papers_sql)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Tables created (or already exist).")


# Path to your SQLite database
db_path = '/Users/kylecondron/Documents/coding/science/arxiv.db'

# Call the function to create the tables
create_tables(db_path)
