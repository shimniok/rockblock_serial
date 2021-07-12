const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http, {
  cors: {
    origin: 'http://localhost:4200',
    methods: ['GET', 'POST'],
    credentials: true,
  },
});
const path = require('path');
const messaging = require('./messaging.service');

// Temporary Data Store
var messages = [];
var signal = 0;

app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname, 'angular-build', 'index.html'));
});


messaging.receive('inbox', function(key, data) {
  switch (key) {
    case "status":
      console.log("status", data);
      break;
    case "signal":
      console.log("signal", data);
      io.emit("signal", data);
      break;
    default:
      console.log("unknown key:", key);
      break;
  }
}, true);


io.on('connection', (socket) => {
  socket.on('send', (message) => {
    console.log('send');
    // add to message store
    // send to rbdaemon somehow
  });

  // send current list of messages
  io.emit('messages', messages);

  // send current signal
  io.emit('signal', signal);

  console.log(`Socket ${socket.id} has connected`);
});

var listener = http.listen(process.env.PORT || 4444, () => {
  console.log('Listening on port ' + listener.address().port);
});
