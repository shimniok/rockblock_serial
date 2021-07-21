import os
import sys
import time
from event_logging import EventLog
from serial.serialutil import SerialException
from rblib import RockBlock
from event_logging import EventLog
from rbd_event_handler import RBDEventHandler


class RockBlockDaemon(RBDEventHandler):

    def __init__(self, device=None, polling_interval=5, log_level=EventLog.DEBUG, event_handler=None):
        self.log = EventLog(level=log_level)
        self.polling_interval = polling_interval

        if not event_handler:
            raise ValueError("event_handler not defined")

        self.cb = event_handler

        self.mo_message = None

        try:
            self.log.info("initialize serial")
            self.rb = RockBlock(device, self)
        except SerialException as e:
            self.log.error("serial: {}".format(e))
            sys.exit(1)
        return

    #
    # Events
    #

    def on_receive(self, message):
        ''' Called when a MT message is received '''
        self.log.info("received MT message: <{}>".format(message))
        self.cb.on_receive(message)
        return

    def on_sent(self, message):
        ''' Called when client requests to send MO message '''
        self.log.info("sent MO message: <{}>".format(message))
        self.cb.on_sent(message)
        return

    def on_ready_to_send(self):
        ''' Called when daemon is ready to dequeue message to send '''
        message = self.cb.on_ready_to_send()
        if message:
            self.log.info("ready to send: <{}>".format(message))
        else:
            self.log.debug("outbox queue empty")
        return message

    def on_signal(self, signal):
        ''' Called when signal strength updated '''
        self.log.debug("signal={}".format(signal))
        self.cb.on_signal(signal)
        return

    def on_serial(self, message):
        ''' Callback for serial text input/output '''
        self.log.debug(" > {}".format(message))
        # self.cb.on_serial(text)
        return

    def on_status(self, status):
        ''' Called when new status available '''
        self.log.debug("status: mo_flag={} mt_flag={} ring={}".format(
            status.mo_flag, status.mt_flag, status.ring))
        # self.cb.on_status(status)
        return

    def on_session_status(self, status):
        ''' Called when session status available '''
        self.log.debug("session: mo_flag={} mt_flag={} mt_length={} waiting={}".format(
            status.mo_flag,
            status.mt_flag,
            status.mt_length,
            status.waiting))
        # self.cb.on_session_status(status)
        return

    def on_error(self, text):
        self.log.error(text)
        # self.cb.on_error(text)
        return

    #
    # Other Stuff
    #
    
    def _retrieve_mt_message(self):
        self.log.debug("reading mt buffer")
        msg = self.rb.read_mt_buffer()
        if msg:
            self.on_receive(msg)
            self.rb.clear_mt_buffer()
        return

    def _send_and_receive(self):
        try:
            self.log.debug("getting signal strength")
            signal = self.rb.get_signal_strength()
            self.on_signal(signal)

            # any incoming or outgoing messages?
            self.log.debug("getting status")
            status = self.rb.get_status()
            self.on_status(status)

            # incoming message in buffer
            if status.mt_flag > 0:
                self._retrieve_mt_message()

            # no outgoing messages, check queue
            if status.mo_flag == 0:
                self.log.debug("check queue")
                self.mo_message = self.on_ready_to_send()
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
                    self.on_sent(self.mo_message)
                    self.clear_mo_buffer()

                # MT message successfully received from the GSS.
                if status.mt_status == 1 and status.mt_length > 0:
                    self._retrieve_mt_message()

                if status.mo_status > 4 or status.mt_status > 4:
                    self.on_error("session error: mo_status={} mt_status={}".format(
                        status.mo_status, status.mt_status))

        except SerialException as e:
            self.log.error("serial error: {}".format(e))
            # TODO: automatic reconnect
            pass
        
        except Exception as e:
            self.log.error(e)
            pass

    def enqueue_mo_message(self, message):
        ''' Enqueue an MO message to be sent later '''
        self.outbox.enqueue_message(message)
        return

    def run(self):
        self.log.info("serial polling loop begin")
        try:
            while True:
                self._send_and_receive()
                self.log.debug("sleeping")
                time.sleep(self.polling_interval)
        except KeyboardInterrupt:
            self.log.info("interrupt received, exiting")
            pass
    

if __name__ == "__main__":
    daemon = RockBlockDaemon(device="/dev/ttyUSB0")
    daemon.run()
