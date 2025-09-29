from domain.LogEntry import LogEntry
from utils.collector import Collector

LOG_SOURCES = "data/log_sources.txt"
DB_PATH = "data/Sqlite3.db"

def main():
    collector = Collector(LOG_SOURCES, DB_PATH)
    collector.display_entries()

if __name__ == '__main__':
    main()