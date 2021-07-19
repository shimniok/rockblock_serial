#!/usr/bin/env node

var amqp = require('amqplib/callback_api');

module.exports = {
  connect: (url, callback) => {
    amqp.connect(url, function (err, connection) {
      if (err) {
        console.log('connect error:', err);
      } else {
        connection.createChannel((err, channel) => {
          callback(channel);
        });
      }
    });
  },

  receive: (channel, queue, durable, recv) => {
    channel.assertQueue(queue, { durable: durable });
    console.log(' [*] Waiting for messages in %s.', queue);
    channel.consume(
      queue,
      function (msg) {
        recv(msg.fields.routingKey, msg.content.toString('utf-8'));
      },
      { noAck: true }
    );
  },
};
