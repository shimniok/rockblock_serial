import socket
import select
import time


def Main():
    server_address = ( "localhost", 9999 )

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)

    # Bind the socket to the port
    server.bind(server_address)
    print('starting up on %s port %s' % server_address)

    # Listen for incoming connections
    server.listen(5)
    
    inputs = [server]
    outputs = []
    
    while inputs:

        # Wait for at least one of the sockets to be ready for processing
        print('\nwaiting for the next event')
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        # Handle inputs
        for s in readable:

            if s is server:
                # A "readable" server socket is ready to accept a connection
                connection, client_address = s.accept()
                print('new connection from', client_address)
                connection.setblocking(0)
                inputs.append(connection)
            else:
                data = s.recv(1024)
                if data:
                    # A readable client socket has data
                    print('received "%s" from %s' % (data, s.getpeername()))
                    #message_queues[s].put(data)
                    # Add output channel for response
                    if s not in outputs:
                        outputs.append(s)


        server.close()
        break    


if __name__ == '__main__':
    Main()
