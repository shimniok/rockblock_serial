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

// message data store
var messages = [
  { "message": "msg1" }
];
var signal = 0;

// API for updating signal strength info
app.get('/signal', function(req, res) {
  console.log("signal");
});

// API for posting a newly-received message
app.get('/receive', function(req, res) {
  console.log('receive');
  // add to messages: messages.push( ??? )
  io.emit('messages', messages); // broadcast to all clients
  res.send("received");
});

app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname, 'angular-build', 'index.html'));
});

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
