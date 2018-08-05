#!/usr/bin/env python

from rockblock import RockBlock, RockBlockProtocol, RockBlockException
import signal
import sys
import threading
import curses
import argparse

        
class RockApp(RockBlockProtocol):

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--device", 
            help="specify serial device to communicate with RockBLOCK", 
            default="/dev/ttyUSB0")
        args = parser.parse_args()
        self.device = args.device
        
        try:
            self.window_init()
            self.event_loop()
        except (KeyboardInterrupt):
            curses.endwin()
            pass

    def window_init(self):
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
        self.w_status_height = 1
        self.w_input_height = 3
        msg_height = maxy - self.w_status_height - self.w_input_height - 2*margin_y + 1
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
        self.win2 = curses.newwin(self.w_input_height, self.width, begin_y, begin_x)
        self.win2.box()
        helptxt = "[q] quit | [s] send message | [r] receive message"
        self.win2.addstr(0, self.center(helptxt), helptxt, self.yellow)
        self.win2.refresh()

        # input sits inside winbot
        self.w_input = curses.newwin(self.w_input_height-2, self.width-2, begin_y+1, begin_x+1)
        self.w_input.refresh()

        begin_y += self.w_input_height

        # status window sits below winbot, no border
        self.w_status = curses.newwin(self.w_status_height, self.width, begin_y, begin_x)
        self.w_status.refresh()


    def event_loop(self):
        # initialize RockBlock interface
        try:
            rb = RockBlock(self.device, self)          
        except RockBlockException as err:
            curses.endwin()
            print("Error: {}: {}\n".format(self.device, err))
            sys.exit(1)

        while (True):
            curses.curs_set(0)
            c = self.w_input.getkey()
            if c == "q":
                rb.close()
                break
            elif c == "s":
                self.w_input.addstr(0, 0, "Message> ")
                curses.curs_set(1)
                curses.echo()
                self.w_input.refresh()
                self.s = self.w_input.getstr() # read message string
                curses.curs_set(0)
                curses.noecho()
                self.w_input.erase()
                self.w_input.refresh()
                self.w_input.move(0,1)
                rb.sendMessage(self.s)
            elif c == "r":
                rb.messageCheck()
        
        curses.endwin()
        #self.timer_stop()
        sys.exit(0)

    def print_status(self, status):
        self.w_status.erase()
        self.w_status.addstr(0,1, status, self.red)
        self.w_status.clrtoeol()
        self.w_status.refresh()

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
        self.win2.addstr(self.w_input_height-1, self.center(self.device), self.device, self.cyan)
        self.win2.refresh()
        return


    def rockBlockDisonnected(self):
        self.win2.addstr(self.w_input_height-1, self.center(self.device), self.device, self.red)
        self.win2.refresh()
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
