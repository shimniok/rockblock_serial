# Architecture for Mobile Rock7 Thingy

## Data Flow

Rock7 <--serial--> RB Daemon <--RabbitMQ--> NodeJS <--websockets--> Angular UI
                                    +---> NodeJS --> db

## Function Flow

 Mobile Terminated (MT) messages raise the *ring* flag on Rock7. RB Daemon detects and then retrieves message. If successful, it publishes the message to a message queue. The Node backend is notified of the new message and in turn persists it and notifies the front end over websockets. The same process occurs whenever a new value for signal strength is parsed by the daemon

 Mobile Originated (MO) messages are sent by the Angular UI over web sockets to the Node backend which in turn persists the message and publishes to a message queue. The RB Daemon, when ready to send a new message, pulls the next item out of the message queue and attempts sending. It reports the status back through a queue which results in status update on the persisted message.

## Technologies

 * Python
 * Angular
 * WebSockets
 * RabbitMQ
 * some kind of db (TBD)

## RabbitMQ Queues

 * Signal Strength: not durable
   * daemon to client
   * 'signal' update signal strength, not persistent
 * Inbox: durable
   * daemon to client
   * 'received' MT messages received, persistent
   * sent messages
 * Outbox: durable
   * client to daemon
   * 'send' send an MO message

## SocketIO Events

  * 'mt_recv' for mt message received
  * 'mo_send' for mo messages to be sent
  * 'signal' for signal strength

## Working notes

 * RabbitMQ backing store
 * any built-in way to track status for a specific message in queue? transactions?
 * [dos and don'ts](https://www.cloudamqp.com/blog/part4-rabbitmq-13-common-errors.html)

Use multiple queues and consumers. Limit queue size with TTL or max-length, if possible. Persistent messages and durable queues for a message to survive a server restart. Consume (push), don’t poll (pull) for messages. [sorry but polling makes the most sense, otherwise I have to add some additional code/mechanism for queueing in which case what is the damn point of having a message queue??]

https://livebook.manning.com/book/rabbitmq-in-depth/chapter-10

 * Publishing AMQP messages from PostgreSQL
 * Making RabbitMQ listen to PostgreSQL notifications

Using RabbitMQ to decouple write operations against OLTP databases is a common way to achieve great data warehousing and event-stream processing techniques. 

Another powerful pattern is for your database to directly publish messages to RabbitMQ. This can be achieved by using extensions or plugins in the database, or by having a RabbitMQ plugin that acts as a database client, ...

pg_amqp PostgreSQL extension ?


