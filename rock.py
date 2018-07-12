#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol
import signal
import sys
import threading

class RockClient(rockBlockProtocol):

    def main(self):
        self.rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
        signal.signal(signal.SIGINT, self.signal_handler)
        self.timer_start()

        while True:
            try:
                text = raw_input("Message?> ").strip()
                if text != "":
                    self.timer.cancel()
                    print("Sending: <{}>".format(text))
                    self.rb.sendMessage(text.strip())
                    self.timer.start()
            except EOFError:
                self.quit()

    def quit(self):
        self.timer_stop()
        print('\nExiting.')
        self.rb.close()
        sys.exit(0)

    def timer_start(self):
        self.timer = threading.Timer(3.0, self.timer_handler)
        self.timer.start()

    def timer_stop(self):
        self.timer.cancel()

    def timer_handler(self):
        print("\nTimer handler <<-- insert mtrecv here")
        self.timer_start()

    def signal_handler(self, sig, frame):
        self.quit()

    def rockBlockTxStarted(self):
        print "rockBlockTxStarted"

    def rockBlockTxFailed(self):
        print "rockBlockTxFailed"

    def rockBlockTxSuccess(self,momsn):
        print "rockBlockTxSuccess " + str(momsn)

if __name__ == '__main__':
    RockClient().main()
