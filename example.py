#!/usr/bin/env python

import sys
import lib.rockBlock as rockBlock
from lib.rockBlock import rockBlockProtocol

class RockBlockControl(rockBlockProtocol):

    def mo_send(self):
        try:
            rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
            rb.sendMessage("Hello World!")      
            rb.close()
        except (rockBlock.rockBlockException):
            print "mo_send: rockBlockException encountered"
        
    def rockBlockTxStarted(self):
        print "rockBlockTxStarted"
        
    def rockBlockTxFailed(self):
        print "rockBlockTxFailed"
        
    def rockBlockTxSuccess(self,momsn):
        print "rockBlockTxSuccess " + str(momsn)
        
    def mt_recv(self):
        try:
            rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
            rb.requestMessageCheck()
            rb.close()
        except (rockBlock.rockBlockException):
            print "mt_recv: rockBlockException encountered"

    def rockBlockRxStarted(self):
        print "rockBlockRxStarted"
        
    def rockBlockRxFailed(self):
        print "rockBlockRxFailed"
        
    def rockBlockRxReceived(self,mtmsn,data):
        print "rockBlockRxReceived " + str(mtmsn) + " " + data
        
    def rockBlockRxMessageQueue(self,count):
        print "rockBlockRxMessageQueue " + str(count)
             
                     
if __name__ == '__main__':
    if len(sys.argv) != 1:
        print "usage: mosend.py message"
        exit(1)
        
    RockBlockControl().mo_send()

