import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2


conn = psycopg2.connect(
    host = "localhost",
    database = os.environ['LOCAL_DB_NAME'],
    user = os.environ['LOCAL_DB_USER'],
    password = os.environ['LOCAL_DB_PASSWORD']
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute('DROP TABLE IF EXISTS current_windows;')
cur.execute("""CREATE TABLE current_windows(
    id serial PRIMARY KEY,
    window_id integer,
    window_state text, 
    window_focused integer,
    tab_id integer,
    title text, 
    url text, 
    fav_url text,
    created_at TIMESTAMP DEFAULT NOW()
);""")


cur.execute('DROP TABLE IF EXISTS sessions;')
cur.execute("""CREATE TABLE sessions(
    id serial PRIMARY KEY,
    session_title text,
    window_id integer,
    tab_title text, 
    tab_url text,
    tab_fav_url text,
    created_at TIMESTAMP DEFAULT NOW()
);""")


conn.commit()
cur.close()
conn.close()

