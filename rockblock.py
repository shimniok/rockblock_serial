#    Copyright 2015 Makersnake
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import glob
import signal
import sys
import time
import serial

class RockBlockEvent(object):
    def __init__(self, value, status):
        self.value = value
        self.status = status

class RockBlockProtocol(object):

    #RAW OUTPUT
    def process_serial(self, text):pass

    #STATUS
    def print_status(self, text, color):pass

    #CONNECTION
    def rockBlockConnected(self):pass
    def rockBlockDisconnected(self):pass

    #NETWORK TIME
    def rockBlockNetworkTime(self, event):pass

    #IMEI
    def imei_event(self, event):pass

    #SIGNAL
    def signal_event(self, event):pass

    #MT
    def rockBlockRxStarted(self):pass
    def rockBlockRxFailed(self):pass
    def rockBlockRxReceived(self, mtmsn, data):pass
    def rockBlockRxMessageQueue(self, count):pass

    #MO
    def rockBlockTxStarted(self):pass
    def rockBlockTxFailed(self):pass
    def rockBlockTxSuccess(self, momsn):pass


class RockBlockException(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "General Error"
        super(RockBlockException, self).__init__(msg)


class RockBlockSerialException(RockBlockException):
    def __init__(self, msg=None):
        if msg is None:
            msg = "Serial Error"
        super(RockBlockSerialException, self).__init__(msg)


class RockBlockPortException(RockBlockException):
    def __init__(self, msg=None):
        if msg is None:
            msg = "Port Config Error"
        super(RockBlockPortException, self).__init__(msg)


class RockBlock(object):

    IRIDIUM_EPOCH = 1399818235000   
    #May 11, 2014, at 14:23:55 (This will be 're-epoched' every couple of years!)
    
    def __init__(self, portId, callback):
        self.s = None
        #print("port={}".format(portId))
        self.portId = portId
        self.callback = callback
        self.autoSession = True     #When True, we'll automatically initiate additional sessions if more messages to download
        self.SIGNAL_THRESHOLD = 2

        # try:
        self.s = serial.Serial(self.portId, 19200, timeout=10)
        if not (self._disableEcho() and self._disableFlowControl and self._disableRingAlerts()):
            self.close()
            raise RockBlockPortException
            
    ##
    # Serial Specific
    ##

    def close(self):
        if self.s != None:
            self.s.close()
            self.s = None

    @staticmethod
    def listPorts():
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        result = []

        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException) as e:
                pass
        return result

    def serial_readline(self):
        text = self.s.readline().strip()
        self.callback.process_serial(text.decode('utf-8'))
        return text

    ##
    # Parsing
    ##
    
    def send_command(self, command):
        self.s.write(command.encode('utf-8') + b'\r')
        self.callback.process_serial(command)

    def expect(self, expected):
        response = ""
        while response == "":
            response = self.serial_readline().decode('utf-8')

        if response.find(expected) >= 0:
            return response.replace(expected, "")
        else:
            return None

    ##
    # RB Protocol Methods
    ##

    def messageCheck(self):
        self._ensureConnectionStatus()
        
        self.callback.rockBlockRxStarted()
        
        if self.connectionOk() and self._perform_session():
            return True
        else:
            self.callback.rockBlockRxFailed()

    def sendMessage(self, msg):
        self._ensureConnectionStatus()
        self.callback.rockBlockTxStarted()
        if self._queueMessage(msg):
            if self.connectionOk():
                if self._perform_session():
                    return True
                else:
                    self.callback.print_status("perform session failed")
            else:
                self.callback.print_status("connectionOK failed")
        else:
            self.callback.print_status("queue message failed")

        self.callback.rockBlockTxFailed()

        return False

    def connectionOk(self):
        self._ensureConnectionStatus()

        #Check valid Network Time
        if not self._isNetworkTimeValid():
            self.callback.rockBlockSignalFail()
            return False

        #Check signal strength
        signal = self.requestSignalStrength()

        return signal > 0

    def _isNetworkTimeValid(self):
        return self.networkTime() != 0

    def _ensureConnectionStatus(self):
        if self.s == None or self.s.isOpen() == False:
            raise RockBlockException("failed connection status")

    ##
    # AT Command Primitives
    ##

    def ping(self):
        self._ensureConnectionStatus()
        self.send_command("AT")
        response = self.expect("OK")
        
        return response != None

    # TODO: update signal status from here
    def requestSignalStrength(self):
        self._ensureConnectionStatus()
        self.send_command("AT+CSQ")
        self.serial_readline()
        response = self.expect("+CSQ:")
        self.expect("OK")
        try:
            signal = int(response)
        except:
            signal = 0
        #print("signal={}".format(signal))
        ev = RockBlockEvent(signal, signal > 0)
        self.callback.signal_event(ev)
        return signal

    def networkTime(self):
        self._ensureConnectionStatus()
        self.send_command("AT-MSSTM")
        response = self.expect("-MSSTM: ")
        self.expect("OK")   #OK
        if not response == None and not "no network service" in response:
            utc = int(response, 16)
            utc = int((self.IRIDIUM_EPOCH + (utc * 90))/1000)
        else:
            utc = 0
        self.callback.rockBlockNetworkTime(RockBlockEvent(utc, True))
        return utc

    def getSerialIdentifier(self):
        self._ensureConnectionStatus()
        self.send_command("AT+GSN")
        self.serial_readline()
        response = self.serial_readline().decode('utf-8')
        self.expect("OK")
        self.callback.imei_event(RockBlockEvent(response, response != None))
        return response


    # One-time initial setup function (Disables Flow Control)
    # This only needs to be called once, as is stored in non-volitile memory
    #
    # Make sure you DISCONNECT RockBLOCK from power for a few minutes after
    # this command has been issued...
    def setup(self):
        self._ensureConnectionStatus()
        #Disable Flow Control
        self.send_command("AT&K0")
        self.expect("OK")
        
        #Store Configuration into Profile0
        self.send_command("AT&W0")
        self.expect("OK")

        #Use Profile0 as default
        self.send_command("AT&Y0")
        self.expect("OK")

        #Flush Memory
        self.send_command("AT*F")
        self.expect("OK")
        return True

    def _queueMessage(self, msg):
        self._ensureConnectionStatus()
        if len(msg) > 340:
            raise RockBlockException("message must be 340 bytes or less")

        command = "AT+SBDWB={:d}".format(len(msg))
        self.send_command(command)
        if self.expect("READY") != None:
                checksum = 0
                for c in msg:
                    checksum += c
                self.s.write( msg )
                self.s.write( checksum >> 8 )
                self.s.write( checksum & 0xFF )
                self.serial_readline()   #BLANK
            self.serial_readline()   #Some number??
                self.serial_readline()   #BLANK
                self.serial_readline()   #OK
            return True
        else:
            self.callback.print_status("READY message not found")
        return False


    def _enableEcho(self):
        self._ensureConnectionStatus()
        self.send_command("ATE1")
        return not self.expect("OK") == None

    def _disableEcho(self):
        self._ensureConnectionStatus()
        self.send_command("ATE0")
        self.serial_readline()
        return not self.expect("OK") == None

    def _disableFlowControl(self):
        self._ensureConnectionStatus()
        self.send_command("AT&K0")
        return not self.expect("OK") == None

    def _disableRingAlerts(self):
        self._ensureConnectionStatus()
        self.send_command("AT+SBDMTA=0")
        return not self.expect("OK") == None

    def _perform_session(self):
        self._ensureConnectionStatus()
        self.send_command("AT+SBDIX")
        # +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MTqueued>
        response = self.expect("+SBDIX: ")
        self.expect("OK")

        if response != None:
            parts = response.split(",")
            moStatus = int(parts[0])
            moMsn = int(parts[1])
            mtStatus = int(parts[2])
            mtMsn = int(parts[3])
            mtLength = int(parts[4])
            mtQueued = int(parts[5])

            #Mobile Originated
            if moStatus <= 4:
                self._clearMoBuffer()
                self.callback.rockBlockTxSuccess( moMsn )
                pass
            else:
                self.callback.rockBlockTxFailed()

            if mtStatus == 1 and mtLength > 0: 
                # SBD message successfully received from the GSS.
                msg = self._read_mt_message()
                if msg != None:
                    self.callback.rockBlockRxReceived(mtMsn, msg)
            
            # TODO: handle mtStatus error values

            self.callback.rockBlockRxMessageQueue(mtQueued)

            #There are additional MT messages to queued to download
            if mtQueued > 0 and self.autoSession == True:
                self._perform_session() # TODO: get rid of recursion

            if moStatus <= 4:
                return True

        return False


    def _read_mt_message(self):
        self._ensureConnectionStatus()
        # Command echo back + \r{2-byte length}{message}{2-byte checksum}
        self.send_command("AT+SBDRB") 

        # response = self.serial_readline()
        # print("data={}".format(response))

        # print("read length")
        
        length = int.from_bytes(self.s.read(2), byteorder='big')
        # print("length={:d}".format(length))
        msg = ""
        if length > 0:
        #    print("read message")
            msg = self.s.read(length)
            # compute checksum
        #    print("compute checksum")
            mysum = 0
            for c in msg:
        #        print("c={ch:c} {ch:d}".format(ch=c))
                mysum += c
            mysum &= 0xffff

        #print("read checksum")
        cksum = int.from_bytes(self.s.read(2), byteorder='big')

        self.expect("OK")

        if length > 0:
        #    # compare checksum
        #    if mysum != cksum:
        #        print("checksum mismatch {:d} {:d}".format(mysum, cksum))
            return msg
        
        return None


    def _clearMoBuffer(self):
        self._ensureConnectionStatus()
        self.send_command("AT+SBDD0")
        r1 = self.expect("0")
        self.serial_readline()  #BLANK
        self.serial_readline()  #OK
        return not r1 == None
