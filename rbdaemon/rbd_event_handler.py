from rblib import RockBlockEventHandler

# interface class for RockBlockDaemon events
class RBDEventHandler(RockBlockEventHandler):
    ''' event handler for RockBlockDaemon, inherits from RockBlockEventHandler '''
    
    # Called when client requests to send MO message
    def on_send(self, text): pass

    # Called when a MT message is received
    def on_receive(self, text): pass

    # Called when signal strength updated 
    def on_signal(self, signal): pass

    # Called when new status available
    #def on_status(self, status): pass

    # Called when session status available 
    def on_session_status(self, status): pass

    # Called when an error must be passed back
    def on_error(self, text): pass

    # process serial bytes that are sent/received to/from RockBlock
    #def process_serial(self, text): pass
