import os

from pika import callback
from rbd import RockBlockDaemon
import threading
import time
import pika
import rblib
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

    # def on_open(self, connection):
    #     ''' handle channel creation once connection open '''
    #     self.connection.channel(on_open_callback=self.on_channel_open)

    # def on_channel_open(self, channel):
    #     ''' handle publication once channel open '''
    #     channel.queue_declare(queue=OUTBOX, durable=True)
    #     channel.basic_publish('test_exchange', 'message body value',
    #                           pika.BasicProperties(content_type='text/plain',
    #                                                delivery_mode=1))
    #     self.connection.close()

    # def publish(self, queue):
    #     creds = pika.PlainCredentials(USER, PASS, True)
    #     params = pika.ConnectionParameters(host=HOST, credentials=creds)
    #     self.connection = pika.SelectConnection(
    #         parameters=params, on_open_callback=self.on_open)

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
            print("{}: attempting to connect to {} on {}".format(self.name, OUTBOX, HOST))
            self.channel = self.connect_channel(OUTBOX)
            print("{}: setting up basic consume on {}".format(self.name, INBOX))
            self.channel.basic_consume(OUTBOX, self.on_send, auto_ack=True)
            print("{}: start consuming...".format(self.name))
            self.channel.start_consuming()
        except Exception as e:
           print("{}: connection error: {}".format(self.name, e))
           time.sleep(5)
        return


class InboxProducer(rblib.RockBlockEventHandler, RabbitClient):
    
    def __init__(self, name, device, queue_dir):
        RabbitClient.__init__(self, name)
        self.rbd = RockBlockDaemon(
            device=device, queue_dir=queue_dir, polling_interval=5, callback=self)
        return

    def publish(self, routing_key, body):
        ''' Publish message to exchange '''
        print("publishing to {}".format(EXCHANGE))
        self.channel.basic_publish(exchange=EXCHANGE,
                                   routing_key=routing_key,
                                   body="{}".format(body))
        return

    def on_receive(self, text):
        ''' Called when a MT message is received '''
        self.publish('mt_recv', text)
        return

    def on_signal(self, signal):
        ''' Called when signal strength updated '''
        self.publish('signal', signal)
        return

    def on_status(self, status):
        ''' Called when new status available'''
        self.publish('status', json.dumps(status.toJSON()))
        return

    def on_session_status(self, status):
        ''' Called when session status available '''
        self.publish('session_status', status)
        return

    def on_error(self, text):
        ''' Called when an error must be passed back '''
        return

    def process_serial(self, text):
        ''' Process serial bytes that are sent/received to/from RockBlock '''
        return

    def run(self):
        ''' Run the rbdaemon with callback to pass data to queue '''
        try:
            print("{}: attempting to connect to {} on {}".format(self.name, INBOX, HOST))
            self.connect_channel(INBOX)
            print("{}: attempting to bind {} to {}".format(self.name, INBOX, EXCHANGE))
            self.channel.exchange_declare(EXCHANGE, durable=True)
            for key in ['signal', 'status', 'session_status', 'mt_recv']:
                self.channel.queue_bind(exchange=EXCHANGE, queue=INBOX, routing_key=key)
        except Exception as e:
            print("{}: connection error: {}".format(self.name, e))
            time.sleep(5)

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
