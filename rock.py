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
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--device", 
            help="unix serial device connected to rockBlock", 
            default="/dev/ttyUSB0")
        args = parser.parse_args()

        begin_x = 2
        begin_y = 1
        msg_height = 15
        input_height = 4
        stat_height = 5
        self.width = 76

        self.scr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()
        self.scr.border(0)

        curses.init_pair(1, curses.COLOR_RED, -1)
        self.red = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        self.green = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        self.cyan = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        self.yellow = curses.color_pair(4)

        # top enclosing window so we can draw a box
        wintop = curses.newwin(msg_height, self.width, begin_y, begin_x)
        wintop.box()
        wintop.refresh()

        # msg sits inside wintop
        self.msg = curses.newwin(msg_height-2, self.width-2, begin_y+1, begin_x+1)
        self.msg.refresh()

        begin_y += msg_height

        # bottom enclosing window so we can draw a box
        winbot = curses.newwin(input_height, self.width, begin_y, begin_x)
        winbot.box()
        helptxt = "[q] quit | [s] send message | [r] receive message"
        winbot.addstr(0, self.center(helptxt), helptxt, self.yellow)
        winbot.addstr(input_height-1, self.center(args.device), args.device, self.cyan)
        winbot.refresh()

        rb = rockBlock.rockBlock(args.device, self)

        # input sits inside winbot
        input = curses.newwin(input_height-2, self.width-2, begin_y+1, begin_x+1)
        input.refresh()

        begin_y += input_height

        # status window sits below winbot, no border
        self.wstat = curses.newwin(stat_height, self.width, begin_y, begin_x)
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


    def right(self, string):
        strlen = len(string)
        if (strlen < self.width):
            right = (self.width - strlen)
        return right


    def center(self, string):
        strlen = len(string)
        if (strlen < self.width):
            center = (self.width/2 - strlen/2)
        return center
        
        
    def rockBlockRxStarted(self):
        self.wstat.erase()
        self.wstat.addstr(0,1,"RX Started")
        self.wstat.clrtoeol()
        self.wstat.refresh()


    def rockBlockRxFailed(self):
        self.wstat.erase()
        self.wstat.addstr(0,1,"RX Failed", self.red)
        self.wstat.clrtoeol()
        self.wstat.refresh()


    def rockBlockRxReceived(self, mtmsn, data):
        self.msg.addstr("base> '{}' #{}\n".format(data, mtmsn), self.green)
        self.msg.refresh()


    def rockBlockRxMessageQueue(self, count):
        self.wstat.addstr(0,1,"Queue: " + str(count))
        self.wstat.clrtoeol()
        self.wstat.refresh()


    def rockBlockTxStarted(self):
        self.wstat.erase()
        self.wstat.addstr("TX Started")
        self.wstat.refresh()


    def rockBlockTxFailed(self):
        self.wstat.erase()
        self.wstat.addstr(0,1,"TX Failed", self.red)
        self.wstat.refresh()


    def rockBlockTxSuccess(self,momsn):
        self.wstat.erase()
        self.wstat.addstr(0,1,"TX Succeeded {}".format(str(momsn)), self.green)
        self.wstat.clrtoeol()
        self.wstat.refresh()
        self.msg.addstr("me> '{}'\n".format(self.s))
        self.msg.refresh()


if __name__ == '__main__':
    RockApp().main()
