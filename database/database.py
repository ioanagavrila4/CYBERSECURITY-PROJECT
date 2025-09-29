import sqlite3

file = "Sqlite3.db"

connection_obj = sqlite3.connect(file)

cursor_obj = connection_obj.cursor()

cursor_obj.execute("DROP TABLE IF EXISTS logs")

table_creation_query = """
    CREATE TABLE logs(
    raw_format VARCHAR(255) NOT NULL,
    time_stamp VARCHAR(255) NOT NULL,
    severity VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    hostname VARCHAR(255) NOT NULL,
    );
"""

cursor_obj.execute(table_creation_query)

connection_obj.close()