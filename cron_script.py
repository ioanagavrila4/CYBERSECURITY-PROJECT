from utils.collector import Collector
import subprocess
import os

LOG_SOURCES = "data/log_sources.txt"
DB_PATH = "data/Sqlite3.db"
JOURNAL_LOG_FILE = "data/journalctl.json"

def main():
    # Step 1: Run journalctl and write output to file (overwrites existing)
    with open(JOURNAL_LOG_FILE, 'w') as f:
        subprocess.run(
            ["journalctl", "-o", "json-pretty", "-r", "-n", "100"],
            stdout=f,
            check=True
        )

    print(f"Exported journalctl logs to {JOURNAL_LOG_FILE}")

    # Step 2: Create collector (reads from LOG_SOURCES and updates DB)
    collector = Collector(LOG_SOURCES, DB_PATH)
    print(collector.get_entry_count())

    # Step 3: Delete the file
    if os.path.exists(JOURNAL_LOG_FILE):
        os.remove(JOURNAL_LOG_FILE)
        print(f"Deleted {JOURNAL_LOG_FILE}")


if __name__ == '__main__':
    main()