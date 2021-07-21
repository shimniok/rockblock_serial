#!/usr/bin/env node

var amqp = require("amqplib/callback_api");

var me = "amqp service";

module.exports = {
  reconnect: (url, callback) => {
    new Promise((resolve) => {
      setTimeout(resolve, 10000);
    }).then(() => {
      module.exports.connect(url, callback);
    });
  },

  connect: (url, callback) => {
    console.log("%s: connecting", me);
    amqp.connect(url, function (err, connection) {
      if (err) {
        console.log("%s: connect error:", me, err);
        module.exports.reconnect(url, callback);
      } else {
        console.log("%s: connected", me);
        connection.createChannel((err, channel) => {
          console.log("%s: channel created", me);

          channel.on("close", () => {
            console.log("%s: channel closed", me);
            module.exports.reconnect(url, callback);
          });

          channel.on("error", (err) => {
            console.log("%s: channel error: %s", err);
          });

          callback(channel);
        });
      }
    });
  },

  receive: (channel, queue, durable, recv) => {
    channel.assertQueue(queue, { durable: durable });
    console.log("%s: [*] Waiting for messages in %s.", me, queue);
    channel.consume(
      queue,
      function (msg) {
        recv(msg.fields.routingKey, msg.content.toString("utf-8"));
      },
      { noAck: true }
    );
  },

  send: (channel, message) => {
    if (channel)
      channel.sendToQueue("outbox", Buffer.from(message));
  }
};
