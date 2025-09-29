import json

UNKNOWN = 0
JSON = 1


class LogEntry:
    def __init__(self, raw_format: str):
        self._raw_format = raw_format
        self._timestamp = None
        self._severity = None
        self._description = None
        self._hostname = None
        self._type = JSON

        if self._type==JSON:
            self.parse_json_log()

    def parse_json_log(self):
        try:
            log = json.loads(self._raw_format)
            self._timestamp = log.get("__REALTIME_TIMESTAMP")
            self._severity = log.get("PRIORITY")
            self._description = log.get("MESSAGE")
            self._hostname = log.get("_HOSTNAME")
        except:
            print("Failed to parse log entry")


def main():
    test_log = LogEntry('')

if __name__ == "__main__":
    main()