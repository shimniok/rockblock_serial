const app = require("express")();
const http = require("http").Server(app);
// const httpProxy = require('http-proxy');
const io = require("socket.io")(http, {
  cors: {
    origin: "http://localhost:4200/",
    methods: ["GET", "POST"],
    credentials: true,
  },
});
const path = require("path");
const amqpService = require("./amqp.service.js");

var amqpUrl = "amqp://localhost/";

var me = "app server";

// Temporary Data Store
var messages = [];

app.get("/", function (req, res) {
  res.sendFile(path.join(__dirname, "angular-build", "index.html"));
});

// AMQP
amqpService.connect(amqpUrl, (channel) => {

  io.on("connection", (socket) => {
    console.log("%s: socket %s has connected", me, socket.id);

    amqpService.receive(channel, "signal", false, (key, data) => {
      console.log("%s: signal recv key=%s data=%s", me, key, data);
      io.emit("signal", data);
    });

    amqpService.receive(channel, "inbox", true, (key, data) => {
      console.log("%s: signal recv key=%s data=%s", me, key, data);
      messages.push(data);
      io.emit("messages", messages);
    });

    socket.on("send", (message) => {
      console.log("%s: mo send msg=%s", me, message);
      amqpService.send(channel, message);
    });

    socket.on("disconnect", () => {
      console.log("%s: socket disconnected - o nooo!", me);
    });

    socket.on("error", () => {
      console.log("%s: socket error - o nooo!", me);
    });

    // send current list of messages
    io.emit("messages", messages);
  });
});

var listener = http.listen(4444, () => {
  console.log("%s: listening on port %d", me, listener.address().port);
});
