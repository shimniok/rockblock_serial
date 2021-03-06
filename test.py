#!/usr/bin/env python3

from rockblock import RockBlock, RockBlockProtocol, RockBlockException
import sys
import argparse

class RockBlockTest(RockBlockProtocol):
    
    def __init__(self):
        return

    def main(self):

        parser = argparse.ArgumentParser(description='test rockblock.')
        parser.add_argument('--device', nargs=1, metavar='device-name', help='serial device', required=True)
        args = parser.parse_args()

        print("=== Initializing {}".format(args.device[0]))
        rb = RockBlock(args.device[0], self)
        
        # only do this once!!!
        #print("=== Setup")
        #rb.setup()
        
        print("=== Ping")
        rb.ping()
        
        # if rb._queueMessage(b"hello"):
        #     print("success")
        # else:
        #     print("failure")

        # print("{}".format(rb.mo_status_to_string(32)))
        # print("{}".format(rb.mo_status_to_string("18")))

        # print("=== Disable ring alerts")
        # rb._disableRingAlerts()
        
        # print("=== Signal strength")
        # signal = rb.requestSignalStrength()
        
        # print("=== Network time")
        # rb.networkTime()
        
        # print("=== IMEI")
        # rb.getSerialIdentifier()

        # print("=== Network time valid")
        # print(rb._isNetworkTimeValid())

        # try:
        #     print("=== Attempt Session")
        #     rb._perform_session()
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

        # print("=== Read MT Buffer")
        # rb._read_mt_message()


        print("=== Closing")
        rb.close()
        

    def process_serial(self, text):
        print("    <{}>".format(text))
        for c in text.encode('utf-8'):
            print("    0x{char:x} {char:c}".format(char=c))
        return

    def rockBlockNetworkTime(self, event):
        print("#### time: {} status: {}".format(event.value, event.status))
        return

    def imei_event(self, event):
        print("#### imei: {} status: {}".format(event.value, event.status))
        return

    def rockBlockConnected(self):
        return

    def rockBlockDisconnected(self):
        return

    def signal_event(self, event):
        print("#### signal: {} status: {}".format(event.value, event.status))
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
        print("mtmsn:<{}> data: <{}>".format(mtmsn, data))
        return

    def rockBlockRxMessageQueue(self, count):
        return

    def rockBlockTxStarted(self):
        return

    def rockBlockTxFailed(self):
        return

    def rockBlockTxSuccess(self, momsn):
        return

    def status(self, message, status):
        print("{} {}".format( message, status))
        return

if __name__ == '__main__':
    RockBlockTest().main()
