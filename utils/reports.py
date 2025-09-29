import json
import sqlite3
import datetime

from utils.collector import Collector


class Reports:
    def __init__(self, collector):
        self.collector = collector

    def get_raw_logs(self):
        raw_logs = []
        try:
            connection_obj = sqlite3.connect(self.collector._Collector__db_path)
            cursor_obj = connection_obj.cursor()
            cursor_obj.execute('SELECT raw_format FROM logs ORDER BY time_stamp')
            rows = cursor_obj.fetchall()
            raw_logs = [row[0] for row in rows]
            connection_obj.close()
        except sqlite3.Error as e:
            print(f"Database error while fetching: {e}")
        return raw_logs

    def get_realtime(self, timestamp_micro):

        try:
            dt = datetime.fromtimestamp(int(timestamp_micro) / 1_000_000)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return "Invalid timestamp"

    def get_pretty_logs(self):
        pretty_logs = []
        raw_logs = self.get_raw_logs()

        for log in raw_logs:
            try:
                log_json = json.loads(log)

                message = log_json.get("MESSAGE", "N/A")
                priority = log_json.get("PRIORITY", "N/A")
                severity = priority
                facility = log_json.get("SYSLOG_FACILITY", "N/A")
                identifier = log_json.get("SYSLOG_IDENTIFIER", "N/A")
                hostname = log_json.get("_HOSTNAME", "N/A")
                id_machine = log_json.get("_MACHINE_ID", "N/A")

                runtime_scope = log_json.get("_RUNTIME_SCOPE", "N/A")
                realtime_raw = log_json.get("__REALTIME_TIMESTAMP", None)

                realtime = self.get_realtime(realtime_raw) if realtime_raw else "N/A"

                pretty_log = (
                    f"Log with Message: {message}\n"
                    f"Severity/Priority: {severity}\n"
                    f"Syslog Facility and Identifier: {facility} {identifier}\n"
                    f"Hostname: {hostname}\n"
                    f"ID Machine: {id_machine}\n"
                    f"Runtime Scope: {runtime_scope}\n"
                    f"Realtime timestamp: {realtime}"
                )

                pretty_logs.append(pretty_log)
            except json.JSONDecodeError as e:
                continue
        return pretty_logs

    def print_pretty_logs(self):
        pretty_logs = self.get_pretty_logs()

        for i, log in enumerate(pretty_logs, 1):
            print(f"{log}")
            print( "-" * 40)

def main():
    LOG_SOURCES = "../data/log_sources.txt"
    DB_PATH = "../data/Sqlite3.db"

    collector = Collector(LOG_SOURCES, DB_PATH)
    report = Reports(collector)
    report.print_pretty_logs()

if __name__ == '__main__':
    main()