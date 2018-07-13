#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol
import signal
import sys
import threading
import curses

class RockApp(rockBlockProtocol):

    def main(self):

        rb = rockBlock.rockBlock("/dev/ttyUSB0", self)

        begin_x = 5
        begin_y = 1
        msg_height = 30
        input_height = 3
        stat_height = 5
        width = 80

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
        winbot.addstr(0, 15, "[q] quit | [s] send message | [r] receive message")
        winbot.refresh()

        # input sits inside winbot
        input = curses.newwin(input_height-2, width-2, begin_y+1, begin_x+1)
        input.refresh()

        begin_y += input_height

        # status window sits below winbot, no border
        #self.wstat = curses.newwin(stat_height, width, begin_y, begin_x)
        #self.wstat.refresh()

        while (True):
            curses.curs_set(0)
            c = input.getkey()
            if c == "q":
                break
            elif c == "m":
                input.addstr(0, 0, "Message> ")
                curses.curs_set(1)
                curses.echo()
                input.refresh()
                s = input.getstr()
                curses.curs_set(0)
                input.erase()
                input.refresh()
                self.msg.move(0, 0)
                self.msg.addstr("me> {}\n".format(s))
                rb.sendMessage(s)
            elif c == "r":
                self.msg.move(0, 0)
                rb.messageCheck()

        curses.endwin()
        #self.timer_stop()
        rb.close()
        sys.exit(0)

    def rockBlockRxStarted(self):
        self.msg.addstr("RX Started\n")
        self.msg.refresh()

    def rockBlockRxFailed(self):
        self.msg.addstr("RX Failed\n")
        self.msg.refresh()

    def rockBlockRxReceived(self, mtmsn, data):
        self.msg.addstr("base> {1} {0}\n".format(mtmsn, data))

    def rockBlockTxStarted(self):
        self.msg.addstr("TX Started\n")
        self.msg.refresh()

    def rockBlockTxFailed(self):
        self.msg.addstr("TX Failed\n")
        self.msg.refresh()

    def rockBlockTxSuccess(self,momsn):
        self.msg.addstr("TX Succeeded {}\n".format(str(momsn)))
        self.msg.refresh()

if __name__ == '__main__':
    RockApp().main()
