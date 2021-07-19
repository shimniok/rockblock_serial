import pika
from datetime import datetime as dt, tzinfo

class OutboxProducer(object):
    def __init__(self, queue, exchange, host):
        self.name = 'amqp_send_test'
        self.queue = queue
        self.host = host
        self.exchange = exchange
        return

    def connect_channel(self):
        creds = pika.PlainCredentials('guest', 'guest', True)
        params = pika.ConnectionParameters(host=self.host, credentials=creds)
        connection = pika.BlockingConnection(params)
        self.channel = connection.channel()
        return self.channel

    def send(self, message):
        try:
            print("connecting to channel")
            self.channel = self.connect_channel()
            print("declaring exchange")
            self.channel.exchange_declare(self.exchange, durable=True)
            print("binding queue to exchange")
            self.channel.queue_bind(
                exchange=self.exchange, queue=self.queue, routing_key='mt_recv')
            print("publishing message")
            self.channel.basic_publish(
                self.exchange,
                'mt_recv',
                body=message,
            )
            self.channel.close()
        except Exception as e:
            print("{}: connection error: {}".format(self.name, e))
        return


if __name__ == "__main__":
    producer = OutboxProducer(queue='inbox', exchange='rbd_exchange', host='localhost')
    now = dt.now()
    ts = dt.strftime(now, '%H:%M:%S %m/%d/%Y')
    producer.send("test message {}".format(ts))
