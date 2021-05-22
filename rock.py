#!/usr/bin/env python3

from rockblock import RockBlock, RockBlockProtocol, RockBlockException
import signal
import sys
import threading
import curses
import argparse
from curses import wrapper
import math
from appdirs import user_config_dir

class RockApp(RockBlockProtocol):

    helptxt = "[q]uit [m]sg-send [r]eceive-msg [i]mei [s]ignal [b]uf-mo-clr"

    ##
    # MAIN
    ##
    def main(self, stdscr, *args, **kwargs):


        #config_dir = user_config_dir("RockBlockSerial", "BotThoughts")
        #config_file = config_dir + "/preferences.json"

        # TODO: make preferences directory if doesn't exist
        # TODO: load preferences file if exists
        # TODO: save preferences as they are updated in application

        # parser = argparse.ArgumentParser()
        # parser.add_argument("-d", "--device",
        #                     help="specify serial device/port connected to RockBLOCK",
        #                     default="/dev/ttyUSB0")
        # args = parser.parse_args()
        self.device = None
        self.signal = 0
        self.scr = stdscr
        self.window_init()
        self.event_loop()        

    ##
    # INITIALIZE WINDOWS
    ##

    def window_init(self):
        curses.start_color()
        curses.use_default_colors()
        self.scr.border(0)

        # initialize colors
        curses.init_pair(1, curses.COLOR_RED, -1)
        self.red = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        self.green = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        self.cyan = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        self.yellow = curses.color_pair(4)
        curses.init_pair(5, curses.COLOR_WHITE, -1)
        self.white = curses.color_pair(5)

        #
        # compute window sizes to fit screen
        #
        max_height, max_width = self.scr.getmaxyx()

        margin_x = 1
        margin_y = 1

        self.full_width = max_width - 2 * margin_x
        full_height = max_height - 2 * margin_y - 1

        row1_height = 1    # header window
        row3_height = 3    # input window
        row4_height = 15   # status / raw windows

        # message window height
        row2_height = full_height - row1_height - \
            row3_height - row4_height + 1

        col1_width = int(self.full_width / 2)
        col2_width = self.full_width - col1_width

        col1_x = 1
        col2_x = col1_x + col1_width

        row1_y = margin_y                          # header window
        row2_y = row1_y + row1_height    # messages window
        row3_y = row2_y + row2_height    # input window
        row4_y = row3_y + row3_height    # status / raw windows

        # print("max_height={} full_height={}\r\n".format(max_height, full_height))
        # print("row1: y={} h={}\r\n".format(row1_y, row1_height))
        # print("row2: y={} h={}\r\n".format(row2_y, row2_height))
        # print("row3: y={} h={}\r\n".format(row3_y, row3_height))
        # print("row4: y={} h={}\r\n".format(row4_y, row4_height))

        # print("max_width={} full_width={}\r\n".format(max_width, self.full_width))
        # print("col1: x={} w={}\r\n".format(col1_x, col1_width))
        # print("col2: x={} w={}\r\n".format(col2_x, col2_width))

        # header window
        self.w_header = self.scr.subwin(row1_height, self.full_width, row1_y, col1_x)
        #self.w_header.refresh()

        # message window, boxed
        self.msg_box = self.scr.subwin(
            row2_height, self.full_width, row2_y, col1_x)
        self.msg_box.box()
        #self.msg_box.refresh()

        self.w_message = self.scr.subwin(row2_height-2, self.full_width-2, row2_y+1, col1_x+1)
        self.w_message.scrollok(True)
        #self.w_message.refresh()

        # input window, boxed
        self.input_box = self.scr.subwin(row3_height, self.full_width, row3_y, col1_x)
        self.input_box.box()
        self.input_box.addstr(0, self.center(self.helptxt, self.full_width), self.helptxt, self.yellow)
        #self.input_box.refresh()

        self.w_input = self.scr.subwin(
            row3_height-2, self.full_width-2, row3_y+1, col1_x+1)
        #self.w_input.refresh()

        # status on left, 50% width, boxed
        self.box3 = self.scr.subwin(
            row4_height, col1_width, row4_y, col1_x)
        self.box3.box()
        #self.box3.refresh()

        self.w_status = self.scr.subwin(
            row4_height-2, col1_width-2, row4_y+1, col1_x+1)
        self.w_status.scrollok(True)
        #self.w_status.refresh()

        # raw on right, 50% width, boxed
        self.win3 = self.scr.subwin(
            row4_height, col2_width, row4_y, col2_x)
        self.win3.box()
        #self.win3.refresh()

        self.w_raw = self.scr.subwin(
            row4_height-2, col2_width-2, row4_y+1, col2_x+1)
        self.w_raw.scrollok(True)
        #self.w_raw.refresh()

        self.scr.refresh()

    ##
    # UI Utilities
    ##

    def select_port(self):
        port = RockBlock.listPorts()

        title = "Select Serial Port"
        margin = 3
        vmargin = 2
        height = len(port) + 2*vmargin + 2
        width = 50
        maxl = width - 2*margin
        w = curses.newwin(height, width, 1, int(self.full_width/2)-int(width/2))
        w.clear()
        w.border()
        w.addstr(0, self.center(title, width), title, self.yellow)

        curses.curs_set(0)

        w.move(vmargin, margin)
        w.addstr("To select a port, type its letter (a-z):")
        y, x = w.getyx()
        y += 2
        
        portlist = {}
        for i in range(len(port)):
            w.move(i+y, margin)
            c1 = i+ord("A")
            c2 = i+ord("a")
            portlist[c1] = port[i]
            portlist[c2] = port[i]
            s = "{:c}. {:{w}.{w}}".format(c2, port[i], w=maxl-3)
            w.addstr(s, self.cyan)
            i += 1
            if i >= 15:
                break
            
        w.refresh()

        # input for port selection
        while True:
            c = self.w_input.getkey()
            if (ord(c) in portlist.keys()):
                self.device = portlist[ord(c)]
                break
        
        w.clear()
        w.refresh()
        self.scr.touchwin()
        self.scr.refresh()

    def print_status(self, status, color):
        self.w_status.addstr(status + "\n", color)
        self.w_status.refresh()

    def generate_signal_str(self, signal):
        bars = ['\u2581', '\u2582', '\u2583', '\u2584', '\u2585']
        s = "Signal:["
        for i in range(0, signal):
            s += bars[i]
        for i in range(signal, 5):
            s += "_"
        s += "]"
        return s

    ##
    # EVENT LOOP
    ##

    def event_loop(self):
        # initialize RockBlock interface
        if self.device == None:
            self.select_port()
            
#        try:
        rb = RockBlock(self.device, self)
        rb.connectionOk()
#        except Exception as e:
#            curses.endwin()
#            print("Error: {}: {}\n".format(self.device, e))
#            sys.exit(1)

        while True:
            curses.curs_set(0)
            c = self.w_input.getkey()
            if c == "q": # quit
                rb.close()
                break
            elif c == "s": # get signal strength
                rb.requestSignalStrength()
            elif c == "i": # get IMEI
                imei = rb.getSerialIdentifier()
                self.print_status(imei, self.cyan)
            elif c == "t": # network time
                tm = rb.networkTime()
                self.print_status(str(tm), self.cyan)
            elif c == "b": # clear MO buffer
                if rb._clearMoBuffer():
                    self.print_status("MO buffer clear", self.white)
                else:
                    self.print_status("MO buffer clear fail", self.red)
            elif c == "m": # send message
                self.w_input.addstr(0, 0, "Message> ")
                curses.curs_set(1)
                curses.echo()
                self.w_input.refresh()
                self.s = self.w_input.getstr()  # read message string
                curses.curs_set(0)
                curses.noecho()
                self.w_input.erase()
                self.w_input.refresh()
                self.w_input.move(0, 1)
                rb.sendMessage(self.s)
            elif c == "r": # receive message
                rb.messageCheck()


    ##
    # String alignment
    ##

    def right(self, string, width):
        strlen = len(string)
        if (strlen < width):
            right = (width - strlen) - 1
        return right

    def center(self, string, width):
        strlen = len(string)
        if (strlen < width):
            center = int(width/2 - strlen/2)
        return center

    ##
    # CALLBACKS
    ##

    def process_serial(self, text):
        if text != "":
            y, x = self.w_raw.getyx()
            self.w_raw.addstr(y, x, text+"\n", self.cyan)
            self.w_raw.clrtoeol()
            self.w_raw.refresh()
        return

    def rockBlockRxStarted(self):
        self.print_status("RX Started", self.white)

    def rockBlockRxFailed(self):
        self.print_status("RX Failed", self.red)

    def rockBlockRxReceived(self, mtmsn, data):
        self.w_message.addstr(
            "base> '{}' #{}\n".format(data, mtmsn), self.green)
        self.w_message.refresh()

    def rockBlockRxMessageQueue(self, count):
        self.w_header.addstr(0, 2, "Queue: {}  ".format(str(count)))
        self.w_header.refresh()

    def rockBlockTxStarted(self):
        self.print_status("TX Started", self.white)

    def rockBlockTxFailed(self):
        self.print_status("TX Failed", self.red)

    def rockBlockTxSuccess(self, momsn):
        self.print_status("TX Succeeded {}".format(str(momsn)), self.green)
        # TODO: self.w_message.addstr("me> '{}'\n".format(self.s))
        self.w_message.refresh()

    ##
    # SIGNAL
    ##
    
    def rockBlockSignal(self, event):
        if event.status:
            color = self.green
        else:
            color = self.red
        self.print_status("Signal: {}".format(event.value), color)
    
    def rockBlockSignalFail(self):
        #s = self.generate_signal_str(0)
        #self.w_header.addstr(0, self.right(s, self.full_width), s, self.red)
        #self.w_header.refresh()
        self.print_status("Signal Fail", self.red)
        return

    def rockBlockSignalPass(self):
        self.print_status("Signal Pass", self.green)
        return

    def rockBlockSignalUpdate(self, signal):
        #s = self.generate_signal_str(signal)
        self.print_status("Signal: {}".format(signal), self.white)
        #self.w_header.addstr(0, self.full_width - len(s) - 2, s, color)
        #self.w_header.refresh()
        return

    ##
    # CONNECTION
    ##
    def rockBlockConnected(self):
        self.w_header.addstr(0, self.center(
            self.device, self.full_width), self.device, self.cyan)
        self.w_header.refresh()
        return

    def rockBlockDisonnected(self):
        self.w_header.addstr(0, self.center(
            self.device), self.device, self.red)
        self.w_header.refresh()
        return


##
# MAIN
##
if __name__ == '__main__':
    curses.wrapper(RockApp().main)
