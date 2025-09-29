import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domain.LogEntry import LogEntry


def read_and_parse_syslog(file_path):
    """
    Read the syslog file and parse each JSON log entry using LogEntry class

    Args:
        file_path (str): Path to the syslog file

    Returns:
        list: List of LogEntry objects
    """
    log_entries = []

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
                    log_entries.append(log_entry)
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

    return log_entries


def main():
    # Path to the dummy syslog file
    syslog_file = "dummy-files/rpi_dummy_syslog.txt"

    print(f"Reading syslog file: {syslog_file}")
    log_entries = read_and_parse_syslog(syslog_file)

    print(f"\nParsed {len(log_entries)} log entries:")

    # Display first few entries as examples
    for i, entry in enumerate(log_entries[:5]):
        print(f"\nEntry {i+1}:")
        print(f"  Timestamp: {entry.get_timestamp()}")
        print(f"  Severity: {entry.get_severity()}")
        print(f"  Hostname: {entry.get_hostname()}")
        print(f"  Message: {entry.get_description()}")


if __name__ == "__main__":
    main()