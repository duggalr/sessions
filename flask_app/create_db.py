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
cur.execute('DROP TABLE IF EXISTS browser_window;')
cur.execute("""CREATE TABLE browser_window(
    id serial primary key,
    google_id integer,
    focused boolean,
    state text,
    number_of_tabs integer,
    fetched_timestamp TIMESTAMP DEFAULT NOW()
);""")

cur.execute('DROP TABLE IF EXISTS browser_tab;')
cur.execute("""create table browser_tab(
    id serial primary key,
    google_id integer,
    title text,
    url text,
    favicon_url text,
    is_active boolean,
    fetched_timestamp TIMESTAMP DEFAULT NOW(),
    window_object_id integer not null,
    FOREIGN KEY (window_object_id) REFERENCES browser_window(id)
);""")

cur.execute('DROP TABLE IF EXISTS saved_session;')
cur.execute("""create table saved_session(
    id serial primary key,
    session_name text,
    created_timestamp TIMESTAMP DEFAULT NOW()
);""")

cur.execute('DROP TABLE IF EXISTS saved_session_url;')
cur.execute("""create table saved_session_url(
    id serial primary key,
    title text,
    url text,
    favicon_url text,
    session_object_id integer not null,
    FOREIGN KEY (session_object_id) REFERENCES saved_session(id)
);""")

conn.commit()
cur.close()
conn.close()

