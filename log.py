from datetime import datetime

class MessageLog:
    def __init__(self, filename):
        self.filename = filename

    def log_message(self, message):
        with open(self.filename, "a") as f:
            dt = datetime.strftime(datetime.now(), "%Y-%m-%d %I:%M:%S")
            f.write("{} {}".format(dt, message))
            f.close()

if __name__ == '__main__':
    ml = MessageLog("test.log")
    ml.log_message("testing")
