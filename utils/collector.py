import json
import os
import sys
import sqlite3

# TODO - check if updated column is 1; set updated column to 1 after alert is sent

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
            syslog_identifier TEXT,
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

    def __read_and_parse_jsonlog(self, file_path: str):
        """
        Read the JSON log file and parse each JSON log entry using LogEntry class.
        Supports NDJSON format (one JSON object per line).

        Args:
            file_path (str): Path to the JSON log file

        Returns:
            list of processed LogEntry objects
        """
        logs = []
        try:
            with open(file_path, 'r') as file:
                for line_number, line in enumerate(file, 1):
                    # Skip empty lines
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        # Validate JSON format first
                        json.loads(line)
                        # Create LogEntry object
                        log_entry = LogEntry(line)
                        logs.append(log_entry)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON on line {line_number}: {e}")
                        print(f"Line content: {line[:100]}...")
                        continue
                    except Exception as e:
                        print(f"Failed to create LogEntry from line {line_number}: {e}")
                        continue

        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error reading file: {e}")

        return logs

    def __insert_logs_to_db(self, logs):
        connection_obj = sqlite3.connect(self.__db_path)
        cursor_obj = connection_obj.cursor()

        # Prepare a set of existing timestamps for quick lookup
        cursor_obj.execute("SELECT time_stamp FROM logs")
        existing_timestamps = set(row[0] for row in cursor_obj.fetchall())

        insert_query = """
            INSERT INTO logs (raw_format, time_stamp, severity, description, syslog_identifier)
            VALUES (?, ?, ?, ?, ?)
        """

        new_entries_added = 0
        for entry in logs:
            timestamp = entry.get_timestamp()

            # Skip duplicate timestamps
            if timestamp in existing_timestamps:
                continue

            cursor_obj.execute(insert_query, (
                entry.get_raw_format(),
                timestamp,
                entry.get_severity(),
                entry.get_description(),
                #entry.get_hostname()
                entry.get_syslog_identifier()
            ))

            new_entries_added += 1
            existing_timestamps.add(timestamp)

        connection_obj.commit()
        connection_obj.close()

        if new_entries_added > 0:
            print(f"Added {new_entries_added} new log entries to database")

    """
    def _trigger_alert(self, log_entry):
        try:
            from .alerts import AlertSender
            alert_sender = AlertSender(db_path=self.__db_path)
            alert_sender.send_security_alert(log_entry)
        except Exception as e:
            print(f"Failed to send alert for log entry: {e}")
    """

    def display_entries_on_console(self) -> None:
        try:
            connection_obj = sqlite3.connect(self.__db_path)
            cursor_obj = connection_obj.cursor()

            select_query = "SELECT raw_format, time_stamp, severity, description, syslog_identifier FROM logs ORDER BY time_stamp"
            cursor_obj.execute(select_query)

            rows = cursor_obj.fetchall()
            if not rows:
                print("No log entries found in the database.")
                return

            for i, row in enumerate(rows, 1):
                print(f"Entry {i}:")
                #print(f"  Raw Format: {row[0]}")
                print(f"  Timestamp: {row[1]}")
                print(f"  Severity: {row[2]}")
                print(f"  Description: {row[3]}")
                print(f"  Syslog Identifier: {row[4]}")
                print()

            connection_obj.close()

        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def get_entry_count(self):
        connection_obj = sqlite3.connect(self.__db_path)
        count = connection_obj.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
        connection_obj.close()
        return count