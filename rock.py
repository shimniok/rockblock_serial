#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol
import signal
import sys
import threading
import curses

class RockGui():

    def __init__(self):
        begin_x = 1;
        begin_y = 5
        msg_height = 30;
        input_height = 3;
        width = 80

        self.scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.scr.border(0)

        self.msg = curses.newwin(msg_height, width, begin_y, begin_x)
        self.msg.box()
        self.msg.refresh()

        input = curses.newwin(input_height, width, begin_y+msg_height, begin_x)
        input.box()

        while (True):
            input.addstr(1, 2, "Command> ")
            input.refresh()
            c = input.getkey()
            if c == "q":
                break
            #elif c == "m":

        curses.endwin()

class RockClient(rockBlockProtocol):

    def main(self):
        self.rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
        #self.timer_start()

        self.gui = RockGui()

        self.quit()

    def quit(self):
        #self.timer_stop()
        self.rb.close()
        print('\nExiting.')
        sys.exit(0)

    #def timer_start(self):
        #self.timer = threading.Timer(3.0, self.timer_handler)
        #self.timer.start()

    #def timer_stop(self):
        #self.timer.cancel()

    #def timer_handler(self):
        #print("\nTimer handler <<-- insert mtrecv here")
        #self.timer_start()

    def rockBlockTxStarted(self):
        print "rockBlockTxStarted"

    def rockBlockTxFailed(self):
        print "rockBlockTxFailed"

    def rockBlockTxSuccess(self,momsn):
        print "rockBlockTxSuccess " + str(momsn)

if __name__ == '__main__':
    RockClient().main()
