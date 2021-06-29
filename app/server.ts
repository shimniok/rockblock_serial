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


const messages = [
  { "message": "msg1" }
]; // this will become data store

app.get('/receive', function(req, res) {
  console.log('receive');
  // add to messages
  // messages.push( ??? )
  io.emit('messages', messages); // broadcast to all clients
  res.send("received");
});

app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname, 'angular-build', 'index.html'));
});

io.on('connection', (socket) => {
  // let previousId;
  // const safeJoin = (currentId) => {
  //   socket.leave(previousId);
  //   socket.join(currentId, () =>
  //     console.log(`Socket ${socket.id} joined room ${currentId}`)
  //   );
  //   previousId = currentId;
  // };

  socket.on('send', (message) => {
    console.log('send');
    // add to message store
    // send to rbdaemon somehow
  });

  // socket.on('getDoc', (docId) => {
  //   console.log('getDoc');
  //   safeJoin(docId);
  //   socket.emit('document', documents[docId]);
  // });

  // socket.on('addDoc', (doc) => {
  //   console.log('addDoc');
  //   documents[doc.id] = doc;
  //   safeJoin(doc.id);
  //   io.emit('documents', Object.keys(documents));
  //   socket.emit('document', doc);
  // });

  // socket.on('editDoc', (doc) => {
  //   console.log('editDoc');
  //   documents[doc.id] = doc;
  //   socket.to(doc.id).emit('document', doc);
  // });

  io.emit('messages', Object.keys(messages));

  console.log(`Socket ${socket.id} has connected`);
});

var listener = http.listen(process.env.PORT || 4444, () => {
  console.log('Listening on port ' + listener.address().port);
});
