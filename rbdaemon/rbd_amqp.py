import os
from rbd import RockBlockDaemon
import threading
import time
import pika
import rblib

HOST = os.environ.get('AMQP_HOST')
INBOX = os.environ.get('INBOX')
OUTBOX = os.environ.get('OUTBOX')
USER = os.environ.get('USER')
PASS = os.environ.get('PASS')


class RabbitClient(object):
    def __init__(self, name=None):
        self.name = name
        if not name:
            raise ValueError("name not specified")
        return

    def connect_channel(self, queue):
        print("{}: attempting to connect to {} on {}".format(self.name, queue, HOST))
        creds = pika.PlainCredentials(USER, PASS, True)
        params = pika.ConnectionParameters(host=HOST, credentials=creds)
        connection = pika.BlockingConnection(params)
        self.channel = connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)


class OutboxConsumer(RabbitClient):
    def on_send(self, channel, method, properties, body):
        ''' handles message received from queue '''
        message = body.decode('UTF-8')
        print("{}}: message received: body={}".format(self.name, message))

    def run(self):
        try:
            self.connect_channel(OUTBOX)
            self.channel.basic_consume(
                queue=OUTBOX, on_message_callback=self.on_send, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            print("consumer: connection error: {}".format(e))
            time.sleep(5)
        return


class InboxProducer(rblib.RockBlockEventHandler, RabbitClient):
    def __init__(self, name, device, queue_dir):
        RabbitClient.__init__(self, name)
        self.rbd = RockBlockDaemon(
            device=device, queue_dir=queue_dir, polling_interval=5, callback=self)
        return

    def on_receive(self, text):
        ''' Called when a MT message is received '''
        return

    def on_signal(self, signal):
        ''' Called when signal strength updated '''
        return

    def on_status(self, status):
        ''' Called when new status available'''
        return

    def on_session_status(self, status):
        ''' Called when session status available '''
        return

    def on_error(self, text):
        ''' Called when an error must be passed back '''
        return

    def process_serial(self, text):
        ''' process serial bytes that are sent/received to/from RockBlock '''
        return

    def run(self):
        try:
            print("consumer: attempting to connect to {} on {}".format(INBOX, HOST))
            self.connect_channel(INBOX)
        except Exception as e:
            print("consumer: connection error: {}".format(e))
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
