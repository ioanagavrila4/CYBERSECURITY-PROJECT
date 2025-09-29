import json

UNKNOWN = 0
JSON = 1


class LogEntry:
    def __init__(self, raw_format: str, log_type=JSON):
        self._raw_format = raw_format
        self._timestamp = None
        self._severity = None
        self._description = None
        self._hostname = None
        self._type = log_type

        if self._type==JSON:
            self.parse_json_log()

    def get_raw_format(self):
        return self._raw_format
    def get_timestamp(self):
        return self._timestamp
    def get_severity(self):
        return self._severity
    def get_description(self):
        return self._description
    def get_hostname(self):
        return self._hostname
    def get_type(self):
        return self._type

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
    test_str = json_str = """
    {
        "_SYSTEMD_SLICE": "-.slice",
        "MESSAGE": "run-credentials-systemd\\x2dtmpfiles\\x2dclean.service.mount: Deactivated suc",
        "_EXE": "/usr/lib/systemd/systemd",
        "_HOSTNAME": "pibytes3",
        "__REALTIME_TIMESTAMP": "1759134362452973",
        "_COMM": "systemd",
        "_CAP_EFFECTIVE": "1ffffffffff",
        "_BOOT_ID": "eb295f91d0804552bc6e3441cc1e2bb6",
        "SYSLOG_IDENTIFIER": "systemd",
        "PRIORITY": "6",
        "CODE_FILE": "src/core/unit.c",
        "_RUNTIME_SCOPE": "system",
        "_TRANSPORT": "journal",
        "CODE_FUNC": "unit_log_success",
        "_SYSTEMD_UNIT": "init.scope",
        "_UID": "0",
        "MESSAGE_ID": "7ad2d189f7e94e70a38c781354912448",
        "_MACHINE_ID": "b29f86b72d8042c4bbdcc14aa31d355f",
        "CODE_LINE": "5618",
        "__MONOTONIC_TIMESTAMP": "928790179",
        "_SYSTEMD_CGROUP": "/init.scope",
        "__CURSOR": "s=087efa337c6648a2abe0eed6a087d677;i=4a3;b=eb295f91d0804552bc6e3441cc1e2bb6;",
        "UNIT": "run-credentials-systemd\\x2dtmpfiles\\x2dclean.service.mount",
        "_SOURCE_REALTIME_TIMESTAMP": "1759134362452958",
        "TID": "1",
        "_PID": "1",
        "_CMDLINE": "/sbin/init splash",
        "SYSLOG_FACILITY": "3",
        "_GID": "0",
        "INVOCATION_ID": "95055cf5adbd4cb3bb661d3468b13cf0"
    }
    """
    test_log = LogEntry(test_str)
    print(test_log.get_severity())


if __name__ == "__main__":
    main()