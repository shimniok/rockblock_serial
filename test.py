#!/usr/bin/env python3

from rockblock import RockBlock, RockBlockProtocol, RockBlockException
import sys


class RockBlockTest(RockBlockProtocol):

    def __init__(self):
        return

    def main(self):
        
        print("=== Initializing")
        rb = RockBlock("/dev/ttyUSB0", self)
        
        print("=== Disable ring alerts")
        rb._disableRingAlerts()
        
        print("=== Signal strength")
        signal = rb.requestSignalStrength()
        print("Signal: {:d}".format(signal))
        
        print("=== Network time")
        print("{}".format(rb.networkTime()))

        print("=== Network time valid")
        print(rb._isNetworkTimeValid())

        # try:
        #     print("=== Attempt Session")
        #     rb._attemptSession()
        # except Exception as e:
        #     print(str(e))
        #     pass

        # #moStatus, moMsn, mtStatus, mtMsn, mtLength, mtQueued
        # print("moStatus: {}".format(rb.moStatus))
        # print("moMsn: {}".format(rb.moMsn))
        # print("mtStatus: {}".format(rb.mtStatus))
        # print("mtMsn: {}".format(rb.mtMsn))
        # print("mtLength: {}".format(rb.mtLength))
        # print("mtQueued: {}".format(rb.mtQueued))

        # print("=== Process MT Message")
        # rb._processMtMessage()
        
        print("=== Closing")
        rb.close()
        

    def process_serial(self, text):
        print("<{}>".format(text))
        for c in text.encode('utf-8'):
            print("{char:d} {char:c}".format(char=c))
        return

    def rockBlockConnected(self):
        return

    def rockBlockDisconnected(self):
        return

    def rockBlockSignalUpdate(self, signal):
        return

    def rockBlockSignal(self):
        return

    def rockBlockSignalFail(self):
        return

    def rockBlockRxStarted(self):
        return

    def rockBlockRxFailed(self):
        return

    def rockBlockRxReceived(self, mtmsn, data):
        return

    def rockBlockRxMessageQueue(self, count):
        return

    def rockBlockTxStarted(self):
        return

    def rockBlockTxFailed(self):
        return

    def rockBlockTxSuccess(self, momsn):
        return


if __name__ == '__main__':
    RockBlockTest().main()
