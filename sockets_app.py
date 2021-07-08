from flask import Flask
from flask_sockets import Sockets


app = Flask(__name__)
sockets = Sockets(app)


@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)
        

@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'


# /notify -> POST -> notify of event (queue contents changed)
@app.route('/notify', methods=['POST'])
def notify():
    ''' external clients use this api to notify ws clients of an event'''
    return 'Hello World!'


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

