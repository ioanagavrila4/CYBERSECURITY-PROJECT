import json
import sqlite3
import datetime

from domain.LogEntry import LogEntry, JSON
from utils.collector import Collector


class Reports:
    def __init__(self, collector):
        self.collector = collector

    def get_log_entries(self):
        """
        function for log entries in detail
        :return:
        """
        log_entries = []
        try:
            connection_obj = sqlite3.connect(self.collector._Collector__db_path)
            cursor_obj = connection_obj.cursor()
            cursor_obj.execute('SELECT raw_format FROM logs ORDER BY time_stamp')
            rows = cursor_obj.fetchall()
            for row in rows:
                raw_log = row[0]
                # Create and store LogEntry object for each raw log string
                log_entry = LogEntry(raw_log, log_type=JSON)
                log_entries.append(log_entry)
            connection_obj.close()
        except sqlite3.Error as e:
            print(f"Database error while fetching logs: {e}")
        return log_entries

    def get_pretty_logs(self):
        """
        function for pretty logs in detail
        :return:
        """
        pretty_logs = []
        log_entries = self.get_log_entries()

        for log_entry in log_entries:
            pretty_log = (
                f"Log with Message: {log_entry.get_description() or 'N/A'}\n"
                f"Severity/Priority: {log_entry.get_severity() or 'N/A'}\n"
                f"Hostname: {log_entry.get_hostname() or 'N/A'}\n"
                f"Realtime timestamp: {log_entry.get_realtime()}"
            )
            pretty_logs.append(pretty_log)

        return pretty_logs

    def print_pretty_logs(self):
        for log in self.get_pretty_logs():
            print(log)
            print("-" * 40)

    def filter_by_type_report(self, type_report, filter_by_this):
        """
        function for filtering log entries by type
        :param type_report:
        :return:
        """
        all_logs = self.get_pretty_logs()
        filtered_logs = []
        for log_entry in all_logs:
            if type_report == "Severity" :
                if log_entry.get_severity() == filter_by_this:
                    filtered_logs.append(log_entry)
            elif type_report == "Time" :
                if log_entry.get_time() < filter_by_this:
                    filtered_logs.append(log_entry)
        return filtered_logs

def main():
    LOG_SOURCES = "../data/log_sources.txt"
    DB_PATH = "../data/Sqlite3.db"

    collector = Collector(LOG_SOURCES, DB_PATH)
    report = Reports(collector)
    report.print_pretty_logs()

if __name__ == '__main__':
    main()