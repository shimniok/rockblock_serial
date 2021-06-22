from datetime import datetime
import os
import re


class FileQueue:
    fname_fmt = "%Y%m%d-%H%M%S+%f.txt"

    def __init__(self, directory):
        self.dir = directory

        # make dir if doesn't exist
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

    def get_filename(self):
        return datetime.strftime(datetime.utcnow(), self.fname_fmt)

    def enqueue_message(self, text):
        file = "{}/{}".format(self.dir, self.get_filename())
        with open(file, mode="w") as f:
            f.write(text)
            f.close()
        return

    def dequeue_message(self):
        all = sorted(os.listdir(self.dir))
        if len(all) == 0:
            return None

        p = re.compile("^\d{8}-\d{6}\+\d{6}.txt")
        files = [f for f in all if p.match(f)]
        #for f in files:
        #    print(f)

        head = "{}/{}".format(self.dir, files[0])

        #print("> {}".format(head))

        with open(head, "r") as m:
            text = m.read()
            m.close()
            os.remove(head)
            return text


if __name__ == "__main__":
    q = FileQueue("./outbox")
    q.enqueue_message(datetime.strftime(datetime.utcnow(), q.fname_fmt))
    msg = q.dequeue_message()
    print(msg)
