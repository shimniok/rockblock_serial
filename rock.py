#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol
import signal
import sys
import threading
import curses

class RockGui():

    def __init__(self):
        begin_x = 5;
        begin_y = 1
        msg_height = 30;
        input_height = 3;
        width = 80

        self.scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.scr.border(0)

        wintop = curses.newwin(msg_height, width, begin_y, begin_x)
        wintop.box()
        wintop.refresh()

        msg = curses.newwin(msg_height-2, width-2, begin_y+1, begin_x+1)
        msg.refresh()

        winbot = curses.newwin(input_height, width, begin_y+msg_height, begin_x)
        winbot.box()
        winbot.addstr(0, 15, "[q] quit | [s] send message | [r] receive message")
        winbot.refresh()

        input = curses.newwin(input_height-2, width-2, begin_y+msg_height+1, begin_x+1)
        input.refresh()

        while (True):
            curses.curs_set(0)
            c = input.getkey()
            if c == "q":
                break
            elif c == "m":
                input.addstr(0, 0, "Message> ")
                curses.curs_set(1)
                input.refresh()
                s = input.getstr()
                input.erase()
                # erase
                # send message
                # display stuff in message window

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
