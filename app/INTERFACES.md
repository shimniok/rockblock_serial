# Web Sockets

## Node -> UI

 * signal: update signal
 * message: new message

## UI -> Node

 * send: send a message

# RabbitMQ

## RabbitMQ -> Node

 * signal: update signal
 * message: new message

## Node -> RabbitMQ
 * send: send a message

Use json for transport of all values:
{ signal: 0 }

Incorporate status as part of MO message object; don't need to pass status data back from rbd

Message 
{
  id: some identifier
  type: MO or MT
  timestamp: timestamp
  text: message text
  status: 0 == ok, 1 == pending, 2 == error
  error: mo_status error code
}

Signal
{
  value: 0-5
}

