import re

# client -> 
#  M message - send "message" via RockBlock
# client <- 
#  S [0-5] - signal strength update
#  M message - MT message, "message", received
#  E error - error encountered

class RockBlockDaemonProtocol(object):
    
    def __init__(self):
        return

    def parse(self, line):
        ''' returns event, argument from parsing line '''
        event = None
        args = None
        p = re.compile(r'^\s*([MSE]) (.*)\s*$')
        m = p.match(line)
        if m:
            e = m.group(1)
            a = m.group(2)
            if e == "S":
                p = re.compile(r'^[0-5]$')
                if p.match(a):
                    event = e
                    args = int(a)
            if e == "M" or e == "E":
                event = e
                args = a
        return event, args
    
    def on_request_send(self):
        return

    def on_message_sent(self):
        return

    def on_receive(self, line):
        event, args = self.parse(line)
        if event == "M":
            # TODO: queue incoming message for sending
            pass
        return

    def on_signal(self):
        return
