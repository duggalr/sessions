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
cur.execute('DROP TABLE IF EXISTS window;')
cur.execute("""CREATE TABLE window(
    id serial primary key,
    google_id integer,
    focused boolean,
    state text,
    number_of_tabs integer,
    fetched_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);""")

cur.execute('DROP TABLE IF EXISTS tab;')
cur.execute("""create table tab(
    id serial primary key,
    google_id integer,
    title text,
    url text,
    favicon_url text,
    is_active boolean,
    fetched_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    window_object_id integer not null,
    FOREIGN KEY (window_object_id) REFERENCES window(id)
);""")

conn.commit()
cur.close()
conn.close()
