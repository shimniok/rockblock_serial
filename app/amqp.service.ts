#!/usr/bin/env node

var amqp = require('amqplib/callback_api');

var amqpUrl = 'amqp://localhost/';

module.exports = {
  send: (queue, msg, durable = false) => {
    amqp.connect(amqpUrl, function (error0, connection) {
      if (error0) {
        console.log('send error:', error0);
      } else {
        connection.createChannel(function (error1, channel) {
          if (error1) {
            throw error1;
          }
          channel.assertQueue(queue, {
            durable: durable,
          });
          channel.sendToQueue(queue, Buffer.from(msg));
          console.log(' [x] Sent %s', msg);
        });
        setTimeout(function () {
          console.log("server.ts.send() - disconnecting from amqp");
          connection.close();
          process.exit(0);
        }, 500);
      }
    });
  },

  receive: (queue, durable, recv) => {
    amqp.connect(amqpUrl, function (error0, connection) {
      if (error0) {
        console.log('recv error:', error0);
      }
      connection.createChannel(function (error1, channel) {
        if (error1) {
          throw error1;
        }
        channel.assertQueue(queue, {
          durable: durable,
        });
        console.log(
          ' [*] Waiting for messages in %s. To exit press CTRL+C',
          queue
        );
        channel.consume(
          queue,
          function (msg) {
            recv(
              msg.fields.routingKey,
              JSON.parse(msg.content.toString('utf-8'))
            );
          },
          { noAck: true }
        );
      });
    });
  },
};
