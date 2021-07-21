import os
import time
import pika
import json
from rbd import RockBlockDaemon
from rbd_event_handler import RBDEventHandler
from event_logging import EventLog

HOST = os.environ.get('AMQP_HOST')
INBOX_QUEUE = os.environ.get('INBOX_QUEUE')
OUTBOX_QUEUE = os.environ.get('OUTBOX_QUEUE')
SIGNAL_QUEUE = os.environ.get('SIGNAL_QUEUE')
USER = os.environ.get('USER')
PASS = os.environ.get('PASS')
EXCHANGE = 'rbd_exchange'


class RBRabbitMQClient(RBDEventHandler):

    channel = None

    def __init__(self, device=None, log_level=EventLog.DEBUG):
        self.name = "rbd/amqp"
        self.device = device
        self.log = EventLog(level=EventLog.DEBUG)
        self.rbd = RockBlockDaemon(
            device=self.device,
            polling_interval=5,
            event_handler=self,
            log_level=log_level)

        return

    def publish(self, routing_key, body, expiration_ms=None):
        ''' Publish message to exchange '''
        print("publishing <{k:}> message to <{x:}>".format(
            x=EXCHANGE, k=routing_key))
        message = "{}".format(body)
        if self.channel:
            self.channel.basic_publish(
                EXCHANGE,
                routing_key,
                body=message,
                # properties=properties
            )
        return

    def on_receive(self, message):
        ''' Called when a MT message is received '''
        self.publish('mt_recv', message)
        return

    def on_sent(self, message):
        ''' Called when MO message successfully sent '''
        self.publish('mo_sent', message)
        return

    def on_ready_to_send(self):
        method_frame, header_frame, body = self.channel.basic_get(
            queue=OUTBOX_QUEUE, auto_ack=True)
        return body

    def on_signal(self, signal):
        ''' Called when signal strength updated '''
        self.publish('signal', signal)
        return

    def on_status(self, status):
        ''' Called when new status available'''
        #self.publish('status', json.dumps(status.toJSON()))
        return

    def on_session_status(self, status):
        ''' Called when session status available '''
        #self.publish('session_status', json.dumps(status.toJSON()))
        return

    def on_error(self, text):
        ''' Called when an error must be passed back '''
        #self.publish('error', text)
        return

    def on_serial(self, text):
        ''' Process serial bytes that are sent/received to/from RockBlock '''
        #self.publish('serial', text, expiration_ms=2000)
        return

    def run(self):
        ''' Run the rbdaemon with callback to pass data to queue '''
        try:
            # set up channel and queues
            print("{}: attempting to connect to {} on {}".format(
                self.name, INBOX_QUEUE, HOST))

            creds = pika.PlainCredentials(USER, PASS, True)
            params = pika.ConnectionParameters(host=HOST, credentials=creds)
            connection = pika.BlockingConnection(params)
            self.channel = connection.channel()

            self.channel.queue_declare(queue=OUTBOX_QUEUE, durable=True)
            self.channel.queue_declare(queue=INBOX_QUEUE, durable=True)
            self.channel.queue_declare(queue=SIGNAL_QUEUE, durable=False)

            self.channel.exchange_declare(EXCHANGE, durable=True)
            self.channel.queue_bind(
                exchange=EXCHANGE, queue=INBOX_QUEUE, routing_key='mt_recv')
            self.channel.queue_bind(
                exchange=EXCHANGE, queue=SIGNAL_QUEUE, routing_key='signal')

        except Exception as e:
            print("{}: connection error: {}".format(self.name, e))
            time.sleep(5)

        self.rbd.run()

        return


if __name__ == "__main__":
    print("rbd_amqp: starting")
    time.sleep(10)

    runner = RBRabbitMQClient(device="/dev/ttyUSB0",
                              log_level=EventLog.DEBUG)
    runner.run()
