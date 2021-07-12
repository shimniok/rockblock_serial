from datetime import now
import json

class Message(object):
    def __init__(self, text, type, timestamp=None, status=0, error=''):
        if type == "MO" or type == "MT":
            self.type = type
        else:
            raise(ValueError("illegal message type, must be MO|MT"))

        self.timestamp = timestamp
        self.text = text
        self.status = int(status)
        self.error = error
        return
        
    def fromJSON(self, json):
        raise(NotImplemented("fromJSON not yet implemented"))
        return

    def toJSON(self):
        return json.dumps(self.__dict__)
