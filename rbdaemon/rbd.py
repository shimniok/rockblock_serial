import os
import sys
import time
from event_logging import EventLog
from serial.serialutil import SerialException
from rblib import RockBlock
from file_queue import FileQueue
from event_logging import EventLog
from rbd_event_handler import RBDEventHandler


class RockBlockDaemon(RBDEventHandler):

    def __init__(self, device, queue_dir, polling_interval=5, log_level=EventLog.DEBUG, callback=None):
        self.log = EventLog(level=log_level)
        self.polling_interval = polling_interval
        self.log.info("initialize queue")
        if not os.path.exists(queue_dir):
            os.mkdir(queue_dir)

        self.outbox = FileQueue(queue_dir+"/outbox")
        self.inbox = FileQueue(queue_dir+"/inbox")
        self.sent = FileQueue(queue_dir+"/sent")

        self.mo_message = None

        self.cb = callback

        try:
            self.log.info("initialize serial")
            self.rb = RockBlock(device, self)
        except SerialException as e:
            self.log.error("serial: {}".format(e))
            sys.exit(1)
        return

    def process_serial(self, text):
        ''' Callback for serial text input/output '''
        self.log.debug(" > {}".format(text))
        # if self.cb:
        #     self.cb.process_serial(text)
        return

    def on_receive(self, text):
        ''' Called when a MT message is received '''
        self.log.info("received MT message: <{}>".format(text))
        # if self.cb:
        #     self.cb.on_receive(text)
        return

    def on_sent(self, text):
        ''' Called when client requests to send MO message '''
        self.log.info("sent MO message: <{}>".format(text))
        return

    def on_signal(self, signal):
        ''' Called when signal strength updated '''
        self.log.debug("signal={}".format(signal))
        if self.cb:
            self.cb.on_signal(signal)
        return

    def on_status(self, status):
        ''' Called when new status available '''
        self.log.debug("status: mo_flag={} mt_flag={} ring={}".format(
            status.mo_flag, status.mt_flag, status.ring))
        # if self.cb:
        #     self.cb.on_status(status)
        return

    def on_session_status(self, status):
        ''' Called when session status available '''
        self.log.debug("session: mo_flag={} mt_flag={} mt_length={} waiting={}".format(
            status.mo_flag,
            status.mt_flag,
            status.mt_length,
            status.waiting))
        # if self.cb:
        #     self.cb.on_session_status(status)
        return

    def on_error(self, text):
        self.log.error(text)
        # if self.cb:
        #     self.cb.on_error(text)
        return

    def _retrieve_mt_message(self):
        self.log.debug("reading mt buffer")
        msg = self.rb.read_mt_buffer()
        if msg:
            self.on_receive(msg)
            self.rb.clear_mt_buffer()
            self.inbox.enqueue_message(msg)
        return

    def _send_and_receive(self):
        try:
            self.log.debug("get signal strength")
            signal = self.rb.get_signal_strength()
            self.on_signal(signal)

            # any incoming or outgoing messages?
            self.log.debug("get status")
            status = self.rb.get_status()
            self.on_status(status)

            # incoming message in buffer
            if status.mt_flag > 0:
                self._retrieve_mt_message()

            # no outgoing messages, check queue
            if status.mo_flag == 0:
                self.log.debug("check queue")
                self.mo_message = self.outbox.dequeue_message()
                if self.mo_message:
                    self.log.debug("writing mo buffer")
                    self.rb.write_mo_buffer(self.mo_message)
                    status.mo_flag = 1

            # perform session if incoming and/or outgoing message present
            if status.mo_flag == 1 or status.ring == 1:
                self.log.debug("performing session")
                status = self.rb.perform_session()

                # MO message successfully sent to the GSS.
                if status.mo_status <= 4:
                    self.inbox.enqueue_message(self.mo_message)
                    # self.on_sent(self.mo_message)
                    # self.on_receive(self.mo_message) ?
                    self.clear_mo_buffer()

                # MT message successfully received from the GSS.
                if status.mt_status == 1 and status.mt_length > 0:
                    self._retrieve_mt_message()

                if status.mo_status > 4 or status.mt_status > 4:
                    self.on_error("session error: mo_status={} mt_status={}".format(
                        status.mo_status, status.mt_status))

        except SerialException as e:
            self.log.error("serial: {}".format(e))
            # TODO: automatic reconnect
            pass
        
        except Exception as e:
            self.log.error(e)
            pass

    def run(self):
        self.log.debug("polling loop begin")
        try:
            while True:
                self._send_and_receive()
                self.log.debug("sleeping")
                time.sleep(self.polling_interval)
        except KeyboardInterrupt:
            self.log.info("interrupt received, exiting")
            pass
    

if __name__ == "__main__":
    daemon = RockBlockDaemon("/dev/ttyUSB0", "./q")
    daemon.run()
