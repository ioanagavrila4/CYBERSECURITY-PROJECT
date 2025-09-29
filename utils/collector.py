import json
import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domain.LogEntry import LogEntry

class Collector:
    def __init__(self, log_sources="../data/log_sources.txt", db_path="../data/Sqlite3.db"):
        self.__log_sources = log_sources
        self.__db_path = db_path
        self.__create_table_if_not_exists()

        self.update_db()

    def __create_table_if_not_exists(self):
        connection_obj = sqlite3.connect(self.__db_path)
        cursor_obj = connection_obj.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_format TEXT NOT NULL UNIQUE,
            time_stamp TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT,
            hostname TEXT,
            updated INTEGER NOT NULL DEFAULT 0
        )
        """
        cursor_obj.execute(create_table_query)
        connection_obj.commit()
        connection_obj.close()


    def add_file(self, file_path: str):
        # TODO - detect log format
        with open(self.__log_sources, 'a') as file:
            file.write(file_path + "\n")
        logs =  self.__read_and_parse_jsonlog(file_path)
        self.__insert_logs_to_db(logs)
    def update_db(self):
        with open(self.__log_sources, 'r') as file:
            for log_path in file:
                log_path = log_path.strip()
                if not log_path:
                    break
                logs = self.__read_and_parse_jsonlog(log_path)
                self.__insert_logs_to_db(logs)

    def __read_and_parse_jsonlog(self,file_path:str ):
        """
        Read the syslog file and parse each JSON log entry using LogEntry class

        Args:
            file_path (str): Path to the syslog file

        Returns:
            list of processed LogEntry objects
        """
        logs = []
        try:
            with open(file_path, 'r') as file:
                content = file.read().strip()

                # Parse JSON objects that are separated by }\n{
                # Split by closing brace followed by opening brace
                json_blocks = content.split('}\n{')

                # Fix the split JSON blocks by adding back the braces
                for i, block in enumerate(json_blocks):
                    if not block:
                        continue

                    # Add back the opening brace if it's not the first block
                    if i > 0 and not block.startswith('{'):
                        block = '{' + block

                    # Add back the closing brace if it's not the last block
                    if i < len(json_blocks) - 1 and not block.endswith('}'):
                        block = block + '}'

                    try:
                        # Validate JSON format first
                        json.loads(block)
                        # Create LogEntry object
                        log_entry = LogEntry(block)
                        logs.append(log_entry)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON block {i}: {e}")
                        print(f"Block content: {block[:100]}...")
                        continue
                    except Exception as e:
                        print(f"Failed to create LogEntry from block {i}: {e}")
                        continue

        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error reading file: {e}")

        return logs

    def __insert_logs_to_db(self, logs):
        # TODO ensure no duplicates are added
        connection_obj = sqlite3.connect(self.__db_path)
        cursor_obj = connection_obj.cursor()

        insert_query = """
            INSERT OR IGNORE INTO logs (raw_format, time_stamp, severity, description, hostname)
            VALUES (?, ?, ?, ?, ?)
        """

        new_entries_added = 0
        for entry in logs:
            cursor_obj.execute(insert_query, (
                entry.get_raw_format(),
                entry.get_timestamp(),
                entry.get_severity(),
                entry.get_description(),
                entry.get_hostname()
            ))
            if cursor_obj.rowcount > 0:
                new_entries_added += 1
                # Check if this log needs an alert (severity 5-6)
                if entry.get_severity() in ['5', '6']:
                    self._trigger_alert(entry)

        connection_obj.commit()
        connection_obj.close()

        if new_entries_added > 0:
            print(f"Added {new_entries_added} new log entries to database")

    def _trigger_alert(self, log_entry):
        """Trigger email alert for severity 5-6 logs"""
        try:
            from .alerts import AlertSender
            alert_sender = AlertSender(db_path=self.__db_path)
            alert_sender.send_security_alert(log_entry)
        except Exception as e:
            print(f"Failed to send alert for log entry: {e}")

    def display_entries(self) -> None:
        try:
            connection_obj = sqlite3.connect(self.__db_path)
            cursor_obj = connection_obj.cursor()

            select_query = "SELECT raw_format, time_stamp, severity, description, hostname FROM logs ORDER BY time_stamp"
            cursor_obj.execute(select_query)

            rows = cursor_obj.fetchall()
            if not rows:
                print("No log entries found in the database.")
                return

            for i, row in enumerate(rows, 1):
                print(f"Entry {i}:")
                print(f"  Raw Format: {row[0]}")
                print(f"  Timestamp: {row[1]}")
                print(f"  Severity: {row[2]}")
                print(f"  Description: {row[3]}")
                print(f"  Hostname: {row[4]}")
                print()

            connection_obj.close()

        except sqlite3.Error as e:
            print(f"Database error: {e}")