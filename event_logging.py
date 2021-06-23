from datetime import datetime
from pathlib import Path

class EventLog:

    SILENT = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4

    def __init__(self, filename=None, level=INFO):
        self.filename = filename
        self.set_level(level)
        if filename:
            Path(filename).touch()

    def set_level(self, level):
        if level >= self.SILENT and level <= self.DEBUG:
            self.level = level
        else:
            raise ValueError("invalid level")
        return
    
    def get_level(self):
        return self.level

    def _log(self, text):
        timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %I:%M:%S")
        if self.filename:
            with open(self.filename, "a") as f:
                f.write("{} {}\n".format(timestamp, text))
                f.close()
        else:
            print("{} {}".format(timestamp, text))

    def debug(self, text):
        if self.level >= self.DEBUG:
            self._log("DEBUG: {}".format(text))
        return

    def info(self, text):
        if self.level >= self.INFO:
            self._log("INFO: {}".format(text))
        return

    def warning(self, text):
        if self.level >= self.WARNING:
            self._log("WARNING: {}".format(text))
        return

    def error(self, text):
        if self.level >= self.ERROR:
            self._log("ERROR: {}".format(text))
        return


if __name__ == '__main__':
    ml = EventLog("test.log")
    ml.log("testing")
