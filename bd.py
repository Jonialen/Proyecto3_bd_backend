import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class Database:
    def __init__(self):
        load_dotenv()

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                yield cur
                conn.commit()

