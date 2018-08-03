#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol
import signal
import sys
import threading
import curses
import argparse

class RockApp(rockBlockProtocol):

    def main(self):

        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--device", 
            help="unix serial device connected to rockBlock", 
            default="/dev/ttyUSB0")
        args = parser.parse_args()

        begin_x = 2
        begin_y = 1
        msg_height = 15
        input_height = 3
        stat_height = 5
        width = 76

        self.scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.scr.border(0)

        # top enclosing window so we can draw a box
        wintop = curses.newwin(msg_height, width, begin_y, begin_x)
        wintop.box()
        wintop.refresh()

        # msg sits inside wintop
        self.msg = curses.newwin(msg_height-2, width-2, begin_y+1, begin_x+1)
        self.msg.refresh()

        begin_y += msg_height

        # bottom enclosing window so we can draw a box
        winbot = curses.newwin(input_height, width, begin_y, begin_x)
        winbot.box()
        winbot.addstr(0, msg_height, "[q] quit | [s] send message | [r] receive message")
        winbot.refresh()

        # input sits inside winbot
        input = curses.newwin(input_height-2, width-2, begin_y+1, begin_x+1)
        input.refresh()

        begin_y += input_height

        # status window sits below winbot, no border
        self.wstat = curses.newwin(stat_height, width, begin_y, begin_x)
        self.wstat.refresh()

        while (True):
            curses.curs_set(0)
            c = input.getkey()
            if c == "q":
                break
            elif c == "s":
                input.addstr(0, 0, "Message> ")
                curses.curs_set(1)
                curses.echo()
                input.refresh()
                self.s = input.getstr() # read message string
                curses.curs_set(0)
                curses.noecho()
                input.erase()
                input.refresh()
		input.move(0,1)
                rb.sendMessage(self.s)
            elif c == "r":
                rb.messageCheck()

        curses.endwin()
        #self.timer_stop()
        rb.close()
        sys.exit(0)

    def rockBlockRxStarted(self):
	self.wstat.erase()
        self.wstat.addstr(0,1,"RX Started")
        self.wstat.refresh()

    def rockBlockRxFailed(self):
	self.wstat.erase()
        self.wstat.addstr(0,1,"RX Failed")
        self.wstat.refresh()

    def rockBlockRxReceived(self, mtmsn, data):
        self.msg.addstr("base> ")
        self.msg.addstr("'{}' #{}\n".format(data, mtmsn))
	self.msg.refresh()

    def rockBlockRxMessageQueue(self, count):
        self.wstat.addstr(0,1,"Queue: " + str(count))

    def rockBlockTxStarted(self):
	self.wstat.erase()
        self.wstat.addstr("TX Started")
        self.wstat.refresh()

    def rockBlockTxFailed(self):
	self.wstat.erase()
        self.wstat.addstr(0,1,"TX Failed")
        self.wstat.refresh()

    def rockBlockTxSuccess(self,momsn):
	self.wstat.erase()
        self.wstat.addstr(0,1,"TX Succeeded {}".format(str(momsn)))
        self.wstat.refresh()
        self.msg.addstr("me> '{}'\n".format(self.s))
	self.msg.refresh()

if __name__ == '__main__':
    RockApp().main()
