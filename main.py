from utils.collector import Collector
from utils.alerts import AlertSender
import time

LOG_SOURCES = "data/log_sources.txt"
DB_PATH = "data/Sqlite3.db"


def main():
    collector = Collector(LOG_SOURCES, DB_PATH)
    print(collector.get_entry_count())

    """
    # Start email monitoring for new logs
    alert_sender = AlertSender(db_path=DB_PATH)
    print("\nStarting email monitoring for logs based on configured priority threshold...")
    alert_sender.start_monitoring(interval=30)

    try:
        print("Monitoring active. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        alert_sender.stop_monitoring()
    """

if __name__ == '__main__':
    main()