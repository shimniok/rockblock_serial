import datetime
import os

from rblib import RockBlockEventHandler
from rbd import RockBlockDaemon
from rbd_event_handler import RBDEventHandler
import threading
import time
import pika
import json

HOST = os.environ.get('AMQP_HOST')
INBOX = os.environ.get('INBOX')
OUTBOX = os.environ.get('OUTBOX')
USER = os.environ.get('USER')
PASS = os.environ.get('PASS')
EXCHANGE = 'rbd_exchange'


class RabbitClient(object):
    def __init__(self, name=None):
        self.name = name
        if not name:
            raise ValueError("name not specified")
        return

    def connect_channel(self, queue):
        print("{}: attempting to connect to {} on {}".format(
            self.name, queue, HOST))
        creds = pika.PlainCredentials(USER, PASS, True)
        params = pika.ConnectionParameters(host=HOST, credentials=creds)
        connection = pika.BlockingConnection(params)
        self.channel = connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)
        return self.channel


class OutboxConsumer(RabbitClient):

    def __init__(self, name):
        RabbitClient.__init__(self, name)
        return

    def on_send(self, channel, method, properties, body):
        ''' Handles message received from queue '''
        message = body.decode('UTF-8')
        print("{}: message received: body={}".format(self.name, message))
        # now pass this onto the RockBlock ?

    def run(self):
        ''' Runs the consumer '''
        try:
            print("{}: attempting to connect to {} on {}".format(
                self.name, OUTBOX, HOST))
            self.channel = self.connect_channel(OUTBOX)
            print("{}: setting up basic consume on {}".format(self.name, INBOX))
            self.channel.basic_consume(OUTBOX, self.on_send, auto_ack=True)
            print("{}: start consuming...".format(self.name))
            self.channel.start_consuming()
        except Exception as e:
            print("{}: connection error: {}".format(self.name, e))
            time.sleep(5)
        return


class InboxProducer(RBDEventHandler, RabbitClient):

    channel = None

    def __init__(self, name, device, queue_dir):
        RabbitClient.__init__(self, name)
        self.device = device
        self.queue_dir = queue_dir
        return

    def publish(self, routing_key, body, expiration_ms=None):
        ''' Publish message to exchange '''
        print("publishing <{k:}> message to <{x:}>".format(
            x=EXCHANGE, k=routing_key))

        # timestamp = int(time.time())
        message = "{}".format(body)

        # properties = pika.BasicProperties(
        #     delivery_mode=2,                # makes job persistent
        #     priority=0,                     # default priority
        #     timestamp=timestamp,            # timestamp of job creation
        # )

        #if expiration_ms and expiration_ms.type() == int:
        #    properties.expiration = str(expiration_ms)

        if self.channel:
            self.channel.basic_publish(
                EXCHANGE, routing_key, 
                body=message, 
                #properties=properties
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
            print("{}: attempting to connect to {} on {}".format(
                self.name, INBOX, HOST))
            self.channel = self.connect_channel(INBOX)
            print("{}: attempting to bind {} to {}".format(
                self.name, INBOX, EXCHANGE))
            self.channel.exchange_declare(EXCHANGE, durable=True)
            for key in ['mt_recv', 'signal', 'status', 'session_status', 'error', 'serial']:
                self.channel.queue_bind(
                    exchange=EXCHANGE, queue=INBOX, routing_key=key)
        except Exception as e:
            print("{}: connection error: {}".format(self.name, e))
            time.sleep(5)

        self.rbd = RockBlockDaemon(
            device=self.device, queue_dir=self.queue_dir, polling_interval=5, callback=self)

        self.rbd.run()

        return


if __name__ == "__main__":
    print("rbd_amqp: starting")
    time.sleep(10)

    consumer = OutboxConsumer("consumer")  # todo: cmd line parameters
    consumer_thread = threading.Thread(target=consumer.run)
    consumer_thread.start()

    producer = InboxProducer("producer", "/dev/ttyUSB0", "./q")
    producer.run()
