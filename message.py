class Message(object):
    ''' Message object for async integration with rbd '''

    MO_MESSAGE = 0
    MT_MESSAGE = 1

    STATUS_NEW = 0
    STATUS_QUEUED = 1
    STATUS_SENDING = 2
    STATUS_SEND_ERROR = 3
    STATUS_SENT = 4

    def __init__(self, type, text, timestamp):
        if type == self.MO_MESSAGE or type == self.MT_MESSAGE:
            self.type = type
        else:
            raise ValueError("invalid Message type")
        self.text = text
        self.timestamp = timestamp
        self.error = ""
        self.status = self.STATUS_NEW
        return
