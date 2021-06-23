import os
import re
from datetime import datetime
from event_logging import EventLog

class FileQueue:
    fname_fmt = "%Y%m%d-%H%M%S+%f.txt"

    def __init__(self, directory):
        self.dir = directory

        self.p = re.compile(r'^\d{8}-\d{6}[+]\d{6}\.txt$')
        
        # make dir if doesn't exist
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
            
        self.log = EventLog(filename="{}/q.log".format(self.dir), level=EventLog.DEBUG)
        
        return

    def get_directory(self):
        return self.dir

    def get_filename(self):
        return datetime.strftime(datetime.utcnow(), self.fname_fmt)

    def get_messages(self):
        self.log.debug("get_messages()")
        messages = sorted(os.listdir(self.dir))
        # if len(messages) == 0:
        #     return None
        return [f for f in messages if self.p.match(f)]

    def enqueue_message(self, text):
        self.log.debug("enqueue_message()")
        file = "{}/{}".format(self.dir, self.get_filename())
        with open(file, mode="w") as f:
            f.write(text)
            f.close()
        return

    def dequeue_message(self):
        self.log.debug("dequeue_message()")
        files = self.get_messages()

        if not len(files) > 0:
            return None
        
        self.log.debug("files in queue:")
        for f in files:
            self.log.debug("    {}".format(f))
        self.log.debug("end of list")

        head = "{}/{}".format(self.dir, files[0])

        self.log.debug("queue head: {}".format(head))

        with open(head, "r") as m:
            text = m.read()
            m.close()
            os.remove(head)
            self.log.debug("    contents: {}".format(text))
            return text


if __name__ == "__main__":
    q = FileQueue("./outbox")
    q.enqueue_message(datetime.strftime(datetime.utcnow(), q.fname_fmt))
    msg = q.dequeue_message()
    print(msg)
