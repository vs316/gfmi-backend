# import pyodbc
# from contextlib import contextmanager
# from app.core.config import settings
from app.core.database_sqlite import sqlite_client as dremio_client

# class DremioConnection:
#     def __init__(self):
#         self.connection_string = (
#             f"DRIVER={{Dremio ODBC Driver 64-bit}};"
#             f"HOST={settings.DREMIO_HOST};"
#             f"PORT={settings.DREMIO_PORT};"
#             f"UID={settings.DREMIO_USERNAME};"
#             f"PWD={settings.DREMIO_PASSWORD};"
#             f"DATABASE={settings.DREMIO_DATABASE};"
#         )

#     @contextmanager
#     def get_connection(self):
#         conn = None
#         try:
#             conn = pyodbc.connect(self.connection_string)
#             yield conn
#         except Exception as e:
#             if conn:
#                 conn.rollback()
#             raise e
#         finally:
#             if conn:
#                 conn.close()

#     def execute_query(self, query: str, params: tuple = None):
#         with self.get_connection() as conn:
#             cursor = conn.cursor()
#             if params:
#                 cursor.execute(query, params)
#             else:
#                 cursor.execute(query)

#             # Check if it's a SELECT query
#             if query.strip().upper().startswith("SELECT"):
#                 columns = [column[0] for column in cursor.description]
#                 results = cursor.fetchall()
#                 return [dict(zip(columns, row)) for row in results]
#             else:
#                 conn.commit()
#                 return cursor.rowcount


# dremio_client = DremioConnection()
