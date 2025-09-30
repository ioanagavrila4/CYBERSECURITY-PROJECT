from ui.email_interface import create_email_interface
from utils.collector import Collector
from utils.alerts import AlertSender
import time

LOG_SOURCES = "data/log_sources.txt"
DB_PATH = "data/Sqlite3.db"

def main():
    #TODO execute update_db script on boot
    collector = Collector(LOG_SOURCES, DB_PATH)
    #print(f'DEBUG: Added {collector.get_entry_count()} entries from db')
    #collector.display_entries_on_console()

    create_email_interface()

if __name__ == '__main__':
    main()