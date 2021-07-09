import os
import pika
import time

# host = os.environ.get('AMQP_HOST')
# inbox = os.environ.get('INBOX')
# outbox = os.environ.get('OUTBOX')
host = 'localhost'
inbox = 'inbox'
outbox = os.environ.get('OUTBOX')


def on_inbox(channel, method, properties, body):
    print("channel: {} routing_key: {} body: {}".format(
        channel, method.routing_key, body
    ))
    return


def on_message(channel, method, properties, body):
    ''' handles message received from queue '''
    message = body.decode('UTF-8')
    print("message received: {}".format(message))


def consume(queue):
    ''' connects to rabbitmq, queue, starts consuming '''
    try:
        print("consumer: attempting to connect to {} on {}".format(queue, host))

        connection_params = pika.ConnectionParameters(host=host)
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        channel.queue_declare(queue=queue, durable=True)

        channel.basic_consume(
            queue=queue, on_message_callback=on_inbox, auto_ack=True)

        print('consumer: subscribed to ' + queue + ', waiting for messages...')

        channel.start_consuming()

    except Exception as e:
        print("consumer: connection error: {}".format(e))
        time.sleep(5)


if __name__ == '__main__':
    #time.sleep(10)
    while (True):
        consume(inbox)
