import socket
import select
from queue import Queue, Empty
from threading import Thread


class TcpServer(Thread):
    inputs = []
    outputs = []
    queues = {}

    def __init__(self, host="localhost", port=9999, receive_handler=None):
        ''' start up the server, call run() to begin listening/handling i/o '''
        server_address = (host, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.receive_handler = receive_handler
        self.thread = Thread(target=TcpServer.run, args=[self])

        # Bind the socket to the port
        self.server.bind(server_address)
        print('starting up on %s port %s' % server_address)

        return

    def _close_socket(self, s):
        ''' close a given socket and do associated housekeeping '''
        # Stop listening for input on the connection
        if s in self.outputs:
            self.outputs.remove(s)
        self.inputs.remove(s)
        s.close()
        # Remove message queue
        del self.queues[s]

    def _handle_connection(self, s):
        ''' handle new connection '''
        # A "readable" server socket is ready to accept a connection
        connection, client_address = s.accept()
        print('new connection from', client_address)
        connection.setblocking(0)
        self.inputs.append(connection)
        # Give the connection a queue for data we want to send
        self.queues[connection] = Queue()

    def _handle_receive(self, s):
        ''' handle receive -- either data or connection close '''
        data = s.recv(1024)
        if data:
            # A readable client socket has data
            print('received "%s" from %s' % (data, s.getpeername()))
            # self.queues[s].put(data)
            self.receive_handler(data)
            # # Add output channel for response
            # if s not in self.outputs:
            #     self.outputs.append(s)
        else:
            # Interpret empty result as closed connection
            print('closing', s.getpeername(), 'after reading no data')
            self._close_socket(s)

    def _handle_send(self, s):
        ''' send any queued data '''
        print('handling writable condition for', s.getpeername())
        try:
            next_msg = self.queues[s].get_nowait()
        except Empty:
            # No messages waiting so stop checking for writability.
            print('output queue for', s.getpeername(), 'is empty')
            self.outputs.remove(s)
        else:
            print('sending "%s" to %s' % (next_msg, s.getpeername()))
            s.send(next_msg)

    def broadcast(self, data):
        ''' send data to all clients '''
        # queue data for all connected clients
        print('broadcasting:', data)
        for s in self.inputs:
            if not s is self.server:
                self.queues[s].put(data.encode('utf-8'))
                if s not in self.outputs:
                    self.outputs.append(s)
        return

    def run(self):
        ''' begin listening, handle events, run forever '''
        # Listen for incoming connections
        self.server.listen(5)
        self.inputs = [self.server]

        while self.inputs:
            # Wait for at least one of the sockets to be ready for processing
            #print('\nwaiting for the next event')
            readable, writable, exceptional = select.select(
                self.inputs, self.outputs, self.inputs, 0.05)

            # Handle inputs
            for s in readable:
                if s is self.server:
                    self._handle_connection(s)
                else:
                    self._handle_receive(s)

            for s in writable:
                self._handle_send(s)

            # Handle "exceptional conditions"
            for s in exceptional:
                print('handling exceptional condition for', s.getpeername())
                # Stop listening for input on the connection
                self._close_socket(s)

    def start(self):
        self.thread.start()
        return


if __name__ == '__main__':
    server = TcpServer('localhost', 9999)
    server.start()
