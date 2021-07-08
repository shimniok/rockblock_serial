''' 
Middleware interfacing between chat API and rbd 

events: send, receive, signal, status, session status

client.send() -> chat-api:/send -> on_send() --outbox-queue--> rbd
client.receive <--ws-- chat-api:/receive <--rest-- on_receive() <- rbd
client.signal <--ws-- chat-api:/signal <--rest-- on_signal() <- rbd
client.status <--ws-- chat-api:/status <--rest-- on_status() <- rbd
client.session <--ws-- chat-api:/session <--rest-- on_session_status() <- rbd
client.error <--ws-- chat-api:/error <--rest-- on_error() <- rbd
client.serial <--ws-- chat-api:/serial <--rest-- process_serial() <- rbd
'''

from rbd_events import RBDEventHandler


class MyMiddleWare(RBDEventHandler):

    def on_send(self, text):
        ''' Called when client requests to send MO message '''
        self.log.info("send MO message: <{}>".format(text))
        # stick message in outbox queue
        # how do we get status back?
        return

    def on_receive(self, text):
        ''' Called when a MT message is received '''
        self.log.info("received MT message: <{}>".format(text))
        # call receive API
        return
    
    def on_signal(self, signal):
        ''' Called when signal strength updated '''
        self.log.debug("signal={}".format(signal))
        # call signal api
        return

    def on_status(self, status):
        ''' Called when new status available '''
        self.log.debug("status: mo_flag={} mt_flag={} ring={}".format(
            status.mo_flag, status.mt_flag, status.ring))
        # call status api
        return

    def on_session_status(self, status):
        ''' Called when session status available '''
        self.log.debug("session: mo_flag={} mt_flag={} mt_length={} waiting={}".format(
            status.mo_flag,
            status.mt_flag,
            status.mt_length,
            status.waiting))
        # call session status api
        return

    def on_error(self, text):
        self.log.error(text)
        # call error api
        # how do we link this with any other event??
        return

    def process_serial(self, text):
        self.log.debug(" > {}".format(text))
        # call process serial api
        return
