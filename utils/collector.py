import json
import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domain.LogEntry import LogEntry

class Collector:
    def __init__(self):
        self._log_entries = []

    def add_file(self, file_path: str):
        # TODO - detect log format
        self.__read_and_parse_jsonlog(file_path)

    def __read_and_parse_jsonlog(self,file_path:str ):
        """
        Read the syslog file and parse each JSON log entry using LogEntry class

        Args:
            file_path (str): Path to the syslog file

        Returns:
            None
        """
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
                        self._log_entries.append(log_entry)
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

    def insert_logs_to_db(self, db_path):
        connection_obj = sqlite3.connect(db_path)
        cursor_obj = connection_obj.cursor()

        insert_query = """
            INSERT INTO logs (raw_format, time_stamp, severity, description, hostname)
            VALUES (?, ?, ?, ?, ?)
        """

        for entry in self._log_entries:
            cursor_obj.execute(insert_query, (
                entry.get_raw_format(),
                entry.get_timestamp(),
                entry.get_severity(),
                entry.get_description(),
                entry.get_hostname()
            ))

        connection_obj.commit()
        connection_obj.close()

    def display_entries(self) -> None:
        for i, entry in enumerate(self._log_entries[:5]):
            print(f"\nEntry {i + 1}:")
            print(entry.get_raw_format())


def main():
    syslog_file = "../dummy-files/rpi_dummy_syslog.txt"
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "Sqlite3.db")

    collector = Collector()
    collector.add_file(syslog_file)
    collector.display_entries()

    print("\nInserting parsed logs into database...")
    collector.insert_logs_to_db(db_path)
    print("Insertion complete.")

if __name__ == "__main__":
    main()
