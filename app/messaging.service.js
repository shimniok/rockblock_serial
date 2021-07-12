#!/usr/bin/env node

var amqp = require("amqplib/callback_api");

var messaging = {
  send: function (queue, msg, durable=false) {
    amqp.connect("amqp://localhost", function (error0, connection) {
      if (error0) {
        throw error0;
      }
      connection.createChannel(function (error1, channel) {
        if (error1) {
          throw error1;
        }
        channel.assertQueue(queue, {
          durable: durable,
        });
        channel.sendToQueue(queue, Buffer.from(msg));
        console.log(" [x] Sent %s", msg);
      });
      setTimeout(function () {
        connection.close();
        process.exit(0);
      }, 500);
    });
  },

  receive: function (queue, recv, durable=false) {
    amqp.connect("amqp://localhost", function (error0, connection) {
      if (error0) {
        throw error0;
      }
      connection.createChannel(function (error1, channel) {
        if (error1) {
          throw error1;
        }
        channel.assertQueue(queue, {
          durable: durable,
        });
        console.log(
          " [*] Waiting for messages in %s. To exit press CTRL+C",
          queue
        );
        channel.consume(queue,
          function(msg) {
            recv(msg.fields.routingKey, JSON.parse(msg.content.toString('utf-8')))
          }, { noAck: true });
      });
    });
  },
};

module.exports = messaging;
