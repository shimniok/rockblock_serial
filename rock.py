#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol
import signal
import sys

def signal_handler(sig, frame):
        print('\nExiting.')
        sys.exit(0)

class MoSend(rockBlockProtocol):

    def main(self):
        rb = rockBlock.rockBlock("/dev/ttyUSB0", self)

        signal.signal(signal.SIGINT, signal_handler)

        while True:
            text = raw_input("Message?> ").strip()
            if text != "":
                print("<{}>".format(text))
        rb.sendMessage(text.strip())
        rb.close()

    def rockBlockTxStarted(self):
        print "rockBlockTxStarted"

    def rockBlockTxFailed(self):
        print "rockBlockTxFailed"

    def rockBlockTxSuccess(self,momsn):
        print "rockBlockTxSuccess " + str(momsn)

if __name__ == '__main__':
    MoSend().main()
