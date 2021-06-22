from serial.serialutil import SerialException
from rblib import RockBlock, RockBlockProtocol
from queue import FileQueue
import time
import sys


class RockBlockDaemon(RockBlockProtocol):

    def __init__(self, device, queue_dir, polling_interval=5):
        self.polling_interval = polling_interval
        print("initialize queue")
        self.q = FileQueue(queue_dir)
        try:
            print("initialize serial")
            self.rb = RockBlock(device, self)
        except SerialException as e:
            print("serial: {}".format(e))
            sys.exit(1)
        return

    def process_serial(self, text):
        print(": {}".format(text))
        return

    def on_receive(self, text):
        ''' Called when a MT message is received '''
        print("recv text={}".format(text))
        return

    def on_send(self, text):
        ''' Called when client requests to send MO message '''
        print("send text={}".format(text))
        return

    def on_signal(self, signal):
        ''' Called when signal strength updated '''
        print("signal={}".format(signal))
        return

    def on_status(self, status):
        ''' Called when new status available '''
        print("status: mo_flag={} mt_flag={} ring={}".format(
            status.mo_flag, status.mt_flag, status.ring))
        return

    def run(self):
        print("polling loop begin")
        while True:
            print("get signal strength")
            signal = self.rb.get_signal_strength()
            self.on_signal(signal)

            print("get status")
            status = self.rb.get_status()
            self.on_status(status)

            if status.mt_flag > 0:
                print("reading mt buffer")
                msg = self.rb.read_mt_buffer()
                if msg:
                    self.on_receive(msg)
                    self.rb.clear_mt_buffer()

            if status.mo_flag == 0:
                print("check queue")
                msg = self.q.dequeue_message()
                if msg:
                    print("writing mo buffer")
                    self.rb.write_mo_buffer(msg)
                    status.mo_flag = 1

            if status.mo_flag == 1 or status.ring == 1:
                print("performing session")
                if self.rb.perform_session():
                    self.rb.clear_mo_buffer()

            print("sleeping")
            time.sleep(self.polling_interval)


if __name__ == "__main__":
    daemon = RockBlockDaemon("/dev/ttyUSB0", "./q")
    daemon.run()
