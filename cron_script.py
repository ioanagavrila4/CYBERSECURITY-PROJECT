from utils.alerts import AlertSender
from utils.collector import Collector
import subprocess
import os

LOG_SOURCES = "data/log_sources.txt"
DB_PATH = "data/Sqlite3.db"
JOURNAL_LOG_FILE = "data/journalctl.json"

def main():
    with open(JOURNAL_LOG_FILE, 'w') as f:
        subprocess.run(
            ["journalctl", "-o", "json", "-r", "-n", "100"],
            stdout=f,
            check=True
        )

    print(f"Exported journalctl logs to {JOURNAL_LOG_FILE}")

    collector = Collector(LOG_SOURCES, DB_PATH)
    collector.update_db()
    print(collector.get_entry_count())

    # Start email monitoring for new logs
    alert_sender = AlertSender(db_path=DB_PATH)
    print("\nStarting email monitoring for logs based on configured priority threshold...")
    alert_sender.check_new_logs()

if __name__ == '__main__':
    main()