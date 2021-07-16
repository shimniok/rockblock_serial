const app = require("express")();
const http = require("http").Server(app);
const io = require("socket.io")(http, {
  cors: {
    origin: "http://localhost:4200/",
    methods: ["GET", "POST"],
    credentials: true,
  },
});
const path = require("path");
const messaging = require("./amqp.service");

// Temporary Data Store
var messages = [];

app.get("/", function (req, res) {
  res.sendFile(path.join(__dirname, "angular-build", "index.html"));
});

messaging.receive("signal", false, (key, data) => {
  io.emit("signal", data);
});

messaging.receive("inbox", true, (key, data) => {
  messages.push(data);
  io.emit("messages", messages);
});

io.on("connection", (socket) => {
  socket.on("send", (message) => {
    console.log("send");
    messaging.send("outbox", message, true);
  });

  // send current list of messages
  io.emit("messages", messages);

  console.log(`Socket ${socket.id} has connected`);
});

//var listener = http.listen(process.env.PORT || 4444, (x) => {
var listener = http.listen(4444, (x) => {
  console.log("Listening on port " + listener.address().port, x);
});
