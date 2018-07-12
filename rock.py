#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol
import signal
import sys

class RockClient(rockBlockProtocol):

    def main(self):
        self.rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
        signal.signal(signal.SIGINT, self.signal_handler)

        while True:
            text = raw_input("Message?> ").strip()
            if text != "":
                print("Sending: <{}>".format(text))
                self.rb.sendMessage(text.strip())

    def signal_handler(sig, frame):
        print('\nExiting.')
        self.rb.close()
        sys.exit(0)

    def rockBlockTxStarted(self):
        print "rockBlockTxStarted"

    def rockBlockTxFailed(self):
        print "rockBlockTxFailed"

    def rockBlockTxSuccess(self,momsn):
        print "rockBlockTxSuccess " + str(momsn)

if __name__ == '__main__':
    RockClient().main()
