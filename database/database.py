import sqlite3
import os
file = "Sqlite3.db"
data_dir = os.path.join(os.path.dirname(__file__), "..",  "data")
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, "Sqlite3.db")


connection_obj = sqlite3.connect(db_path)

cursor_obj = connection_obj.cursor()

cursor_obj.execute("DROP TABLE IF EXISTS logs")

table_creation_query = """
    CREATE TABLE logs(
    raw_format VARCHAR(255) NOT NULL,
    time_stamp VARCHAR(255) NOT NULL,
    severity VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    hostname VARCHAR(255) NOT NULL
    );
"""

cursor_obj.execute(table_creation_query)

insert_query = """
    INSERT INTO logs (raw_format, time_stamp, severity, description, hostname)
    VALUES (?, ?, ?, ?, ?)
"""
connection_obj.commit()

order_query = """ 
    SELECT * FROM logs ORDER BY time_stamp;
"""
connection_obj.execute(order_query)


connection_obj.close()