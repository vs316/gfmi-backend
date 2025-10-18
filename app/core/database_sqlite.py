import sqlite3
import os
from contextlib import contextmanager

# this is not being used currently but keeping for future reference


class LocalSQLiteConnection:
    """SQLite connection for local testing"""

    def __init__(self, db_file: str = "gfmi_local.db"):
        self.db_file = db_file
        if not os.path.exists(self.db_file):
            print(f"⚠️  Database file not found: {self.db_file}")
            print("Run 'python local_db_setup.py' first to create the database.")

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Check if it's a SELECT query
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return cursor.rowcount


# Create the SQLite client for local testing
sqlite_client = LocalSQLiteConnection()
