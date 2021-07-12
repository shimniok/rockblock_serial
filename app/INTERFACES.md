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
{
  mo_flag: 0,
  mo_msn: 36,
  mt_flag: 0,
  mt_msn: -1,
  ring: 0,
  waiting: 0 
}

we don't really need to pass back entire status / session status do we? 
the only thing we need is mo_status tied to specific message
