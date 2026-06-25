import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attractions (
            id SERIAL PRIMARY KEY,
            name TEXT,
            city TEXT,
            address TEXT,
            description TEXT,
            category TEXT,
            website TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("景點資料表建立成功！")