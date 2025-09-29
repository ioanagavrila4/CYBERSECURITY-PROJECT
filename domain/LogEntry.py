import json

class LogEntry:
    def __init__(self, raw_format: str):
        self._raw_format = raw_format
        self._timestamp = None
        self._severity = None
        self._description = None
        self._hostname = None



    def parse_json_log(self):
        pass


def main():
    pass

if __name__ == "__main__":
    main()