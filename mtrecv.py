#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol

class MtRecv(rockBlockProtocol):
    def main(self):
        rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
        rb.messageCheck()
        rb.close()

    def rockBlockTxStarted(self):
        print "rockBlockTxStarted"

    def rockBlockTxFailed(self):
        print "rockBlockTxFailed"

    def rockBlockTxSuccess(self,momsn):
        print "rockBlockTxSuccess " + str(momsn)

if __name__ == '__main__':
    MtRecv().main()
