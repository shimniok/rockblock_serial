#!/usr/bin/env python

import rockBlock
from rockBlock import rockBlockProtocol
import signal
import sys
import threading
import curses
import argparse
import time # temporary for delay

        
class RockApp(rockBlockProtocol):

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--device", 
            help="unix serial device connected to rockBlock", 
            default="/dev/ttyUSB0")
        args = parser.parse_args()

        self.scr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()
        self.scr.border(0)

        # compute window sizes to fit screen
        maxy, maxx = self.scr.getmaxyx()
        margin_x = 1
        margin_y = 1
        self.width = maxx - 2*margin_x;
        stat_height = 1
        input_height = 3
        msg_height = maxy - stat_height - input_height - 2*margin_y + 1
        begin_x = margin_x
        begin_y = margin_y

        # initialize colors
        curses.init_pair(1, curses.COLOR_RED, -1)
        self.red = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        self.green = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        self.cyan = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        self.yellow = curses.color_pair(4)

        # top enclosing window so we can draw a box
        win1 = curses.newwin(msg_height, self.width, begin_y, begin_x)
        win1.box()
        win1.refresh()

        # msg window sits inside win1
        self.w_message = curses.newwin(msg_height-2, self.width-2, begin_y+1, begin_x+1)
        self.w_message.scrollok(True)
        self.w_message.refresh()

        begin_y += msg_height

        # bottom enclosing window so we can draw a box
        win2 = curses.newwin(input_height, self.width, begin_y, begin_x)
        win2.box()
        helptxt = "[q] quit | [s] send message | [r] receive message"
        win2.addstr(0, self.center(helptxt), helptxt, self.yellow)
        win2.addstr(input_height-1, self.center(args.device), args.device, self.cyan)
        win2.refresh()

        # initialize rockBlock interface
        rb = rockBlock.rockBlock(args.device, self)

        # input sits inside winbot
        win_input = curses.newwin(input_height-2, self.width-2, begin_y+1, begin_x+1)
        win_input.refresh()

        begin_y += input_height

        # status window sits below winbot, no border
        self.w_status = curses.newwin(stat_height, self.width, begin_y, begin_x)
        self.w_status.refresh()

        while (True):
            curses.curs_set(0)
            c = win_input.getkey()
            if c == "q":
                break
            elif c == "s":
                win_input.addstr(0, 0, "Message> ")
                curses.curs_set(1)
                curses.echo()
                win_input.refresh()
                self.s = win_input.getstr() # read message string
                curses.curs_set(0)
                curses.noecho()
                win_input.erase()
                win_input.refresh()
                win_input.move(0,1)
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
        self.w_status.erase()
        self.w_status.addstr(0,1,"RX Started")
        self.w_status.clrtoeol()
        self.w_status.refresh()


    def rockBlockRxFailed(self):
        self.w_status.erase()
        self.w_status.addstr(0,1,"RX Failed", self.red)
        self.w_status.clrtoeol()
        self.w_status.refresh()


    def rockBlockRxReceived(self, mtmsn, data):
        self.w_message.addstr("base> '{}' #{}\n".format(data, mtmsn), self.green)
        self.w_message.refresh()


    def rockBlockRxMessageQueue(self, count):
        self.w_status.addstr(0,1,"Queue: " + str(count))
        self.w_status.clrtoeol()
        self.w_status.refresh()

    def rockBlockSignalFail(self):
        return

    def rockBlockSignalPass(self):
        return

    def rockBlockSignalUpdate(self, signal):
        return

    def rockBlockConnected(self):
        self.w_status.erase()
        self.w_status.addstr(0,1,"Connected")
        self.w_status.clrtoeol()
        self.w_status.refresh()
        return

    def rockBlockTxStarted(self):
        self.w_status.erase()
        self.w_status.addstr("TX Started")
        self.w_status.refresh()


    def rockBlockTxFailed(self):
        self.w_status.erase()
        self.w_status.addstr(0,1,"TX Failed", self.red)
        self.w_status.refresh()


    def rockBlockTxSuccess(self,momsn):
        self.w_status.erase()
        self.w_status.addstr(0,1,"TX Succeeded {}".format(str(momsn)), self.green)
        self.w_status.clrtoeol()
        self.w_status.refresh()
        self.w_message.addstr("me> '{}'\n".format(self.s))
        self.w_message.refresh()


if __name__ == '__main__':
    RockApp().main()
