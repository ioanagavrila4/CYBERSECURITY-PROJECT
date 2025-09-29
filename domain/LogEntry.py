import json
from datetime import datetime

UNKNOWN = 0
JSON = 1

class LogEntry:
    def __init__(self, raw_format: str, log_type=JSON):
        self._raw_format = raw_format
        self._timestamp = None
        self._severity = None
        self._description = None
        #self._hostname = None
        self._syslog_identifier = None
        self._type = log_type

        if self._type==JSON:
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
            self._timestamp = log.get("__REALTIME_TIMESTAMP")
            self._severity = log.get("PRIORITY")
            self._description = log.get("MESSAGE")
            #self._hostname = log.get("_HOSTNAME")
            self._syslog_identifier = log.get("SYSLOG_IDENTIFIER")
        except:
            print("Failed to parse log entry")




def main():
    pass


if __name__ == "__main__":
    main()