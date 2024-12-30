import json
import mysql.connector

# Add these to Lambda environment variables
DB_HOST = 'test-arxiv.cb6uoe6iipl8.us-east-1.rds.amazonaws.com'
DB_USER = 'admin'
DB_PASSWORD = 'SahajKumar3590'
DB_NAME = 'testarxiv'

def connect_to_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def lambda_handler(event, context):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        if not conn.is_connected():
            return {
                'statusCode': 500,
                'body': json.dumps("Connection error: Unable to connect")
            }
        
        # Example inserting into papers table
        insert_paper_query = """
        INSERT INTO papers (paper_name, summary, date_posted, category, link, source)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        paper_data = ('Example Paper', 'Summary text', '2024-10-28', 'ML', 'http://example.com', 'arxiv')
        cursor.execute(insert_paper_query, paper_data)
        
        # Get the paper_id that was just inserted
        paper_id = cursor.lastrowid
        
        # Example inserting into scored_papers
        insert_scores_query = """
        INSERT INTO scored_papers (paper_id, novel_score, exciting_score, validity_score, personal_score, category)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        scores_data = (paper_id, 85, 90, 95, 88, 'ML')
        cursor.execute(insert_scores_query, scores_data)
        
        conn.commit()
        
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully inserted data!')
        }
        
    except mysql.connector.Error as err:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Database error: {str(err)}")
        }
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()