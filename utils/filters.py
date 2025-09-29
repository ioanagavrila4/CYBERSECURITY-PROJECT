from utils.collector import Collector

class LogFilter:
    """
    Takes a Collector object and returns a list of entries based on different criteria

    - filter by:
        - severity
        - hostname SHOULD HAVE BEEN USER
        -
    """
    def __init__(self, collector: Collector):
        self.__collector = collector

    def filter_by_severity(self, severity):
        pass