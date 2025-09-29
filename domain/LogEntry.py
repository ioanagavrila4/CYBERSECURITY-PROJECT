import json
from datetime import datetime

LOG_TYPE_UNKNOWN = 0
LOGTYPE_JSON = 1

class LogEntry:
    def __init__(self, raw_format: str, log_type=LOGTYPE_JSON):
        self._raw_format = raw_format
        self._timestamp = ""
        self._severity = ""
        self._description = ""
        #self._hostname = None
        self._syslog_identifier = ""
        self._type = log_type

        if self._type==LOGTYPE_JSON:
            self.parse_json_log()

    def get_raw_format(self):
        return self._raw_format
    def get_timestamp(self):
        return self._timestamp
    def get_severity(self):
        return int(self._severity)
    def get_description(self):
        return self._description
    #def get_hostname(self):
        #return self._hostname
    def get_syslog_identifier(self):
        return self._syslog_identifier
    def get_type(self):
        return self._type
    def get_realtime(self):
        dt = datetime.fromtimestamp(int(self._timestamp) / 1000000)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def parse_json_log(self):
        try:
            log = json.loads(self._raw_format)

            # Get timestamp
            self._timestamp = log.get("__REALTIME_TIMESTAMP", "")

            # Get severity
            self._severity = log.get("PRIORITY", "6")

            # Get description - handle if it's a list or other type
            message = log.get("MESSAGE", "")
            if isinstance(message, list):
                # If MESSAGE is a list, join it into a string
                self._description = " ".join(str(m) for m in message)
            elif isinstance(message, dict):
                # If MESSAGE is a dict, convert to JSON string
                self._description = json.dumps(message)
            else:
                # Otherwise treat as string
                self._description = str(message) if message else ""

            # Get syslog identifier
            self._syslog_identifier = log.get("SYSLOG_IDENTIFIER", "unknown")

        except json.JSONDecodeError as e:
            print(f"Failed to parse log entry: {e}")
            self._syslog_identifier = "unknown"
        except Exception as e:
            print(f"Error parsing log entry: {e}")
            self._syslog_identifier = "unknown"

def main():
    pass

if __name__ == "__main__":
    main()