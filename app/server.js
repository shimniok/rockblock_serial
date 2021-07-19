const app = require('express')();
const http = require('http').Server(app);
// const httpProxy = require('http-proxy');
const io = require('socket.io')(http, {
  cors: {
    origin: 'http://localhost:4200/',
    methods: ['GET', 'POST'],
    credentials: true,
  },
});
const path = require('path');
const amqp = require('./amqp.service.js');

var amqpUrl = 'amqp://localhost/';

// Temporary Data Store
var messages = [];

app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname, 'angular-build', 'index.html'));
});

// AMQP
amqp.connect(amqpUrl, function (channel) {
  // SocketIO Events
  io.on('connection', (socket) => {
    amqp.receive(channel, 'signal', false, (key, data) => {
      console.log('server.ts: signal recv key =', key, 'data =', data);
      io.emit('signal', data);
    });

    amqp.receive(channel, 'inbox', true, (key, data) => {
      console.log('server.ts: messages recv key =', key, 'data=', data);
      messages.push(data);
      io.emit('messages', messages);
    });

    // TODO: determine if disconnect after send happens here
    socket.on('send', (message) => {
      console.log('server.ts: mo send');
      channel.sendToQueue('outbox', Buffer.from(message));
    });

    // send current list of messages
    io.emit('messages', messages);

    // TODO: handle connection failure / disconnect
    socket.on('disconnect', function () {
      socket.emit('Socket disconnected - o nooo!');
    });

    console.log(`Socket ${socket.id} has connected`);
  });
});

var listener = http.listen(4444, () => {
  console.log('Listening on port ' + listener.address().port);
});
