#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol

class MtRecv(rockBlockProtocol):
    def main(self):
        rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
        rb.messageCheck()
        rb.close()

    def rockBlockRxStarted(self):
        print "RX Started"

    def rockBlockRxFailed(self):
        print "RX Failed"

    def rockBlockRxReceived(self, mtmsn, data):
	print "RX Received"
	print data
	print mtmsn

if __name__ == '__main__':
    MtRecv().main()
