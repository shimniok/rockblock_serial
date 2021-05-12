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

    #CONNECTION
    def rockBlockConnected(self):pass
    def rockBlockDisconnected(self):pass

    #NETWORK TIME
    def rockBlockNetworkTime(self, event):pass

    #IMEI
    def rockBlockImei(self, event):pass

    #SIGNAL
    def rockBlockSignalUpdate(self, signal):pass
    def rockBlockSignalPass(self):pass
    def rockBlockSignalFail(self):pass

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
        self.portId = portId
        self.callback = callback
        self.autoSession = True     #When True, we'll automatically initiate additional sessions if more messages to download
        self.SIGNAL_THRESHOLD = 2

        # try:
        self.s = serial.Serial(self.portId, 19200, timeout=10)
        if not (self._enableEcho() and self._disableFlowControl and self._disableRingAlerts()):
            self.close()
            raise RockBlockPortException
        self.check_connection()
      
        # except ValueError:
        #     raise RockBlockSerialException("Bad parameters for Serial")
        # except serial.SerialException as e1:
        #     raise RockBlockSerialException("Serial exception {}".format(str(e1)))
        # except Exception as e2:
        #     raise RockBlockException("Other exception in serial init {}".format(str(e2)))
            
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
        echo = self.serial_readline()

    def expect(self, expected):
        response = self.serial_readline().decode('utf-8')
        if response.find(expected) >= 0:
            return response.replace(expected, "")
        else:
            return None

    ##
    # RB Protocol Methods
    ##

    #Handy function to check if connection is still alive, callback based on result
    def check_connection(self):
        self.s.timeout = 5
        if self.ping():
            self.callback.rockBlockConnected()
        else:
            self.callback.rockBlockDisconnected()

    def messageCheck(self):
        self._ensureConnectionStatus()
        
        self.callback.rockBlockRxStarted()
        
        if self.connectionOk() and self._attemptSession():
            return True
        else:
            self.callback.rockBlockRxFailed()

    def sendMessage(self, msg):
        self._ensureConnectionStatus()

        self.callback.rockBlockTxStarted()

        if self._queueMessage(msg) and self.connectionOk():
            if self._attemptSession():
                self.callback.rockBlockTxSuccess()
                return True

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

        self.callback.rockBlockSignalUpdate(signal)

        self.callback.rockBlockSignalFail()
        return False

        if signal >= self.SIGNAL_THRESHOLD:
            self.callback.rockBlockSignalPass()
            return True
        else:
            self.callback.rockBlockSignalFail()
            return False

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

    def requestSignalStrength(self):
        self._ensureConnectionStatus()
        self.send_command("AT+CSQ")
        self.serial_readline()
        response = self.expect("+CSQ:")
        self.serial_readline()
        self.expect("OK")

        try:
            signal = int(response)
        except:
            signal = 0
        
        return signal

    def networkTime(self):
        self._ensureConnectionStatus()
        self.send_command("AT-MSSTM")
        response = self.expect("-MSSTM: ")
        self.serial_readline()   #BLANK
        self.serial_readline()   #OK
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
        response = self.serial_readline().decode('utf-8')
        self.serial_readline()   #BLANK
        self.serial_readline()   #OK
        self.callback.rockBlockImei(RockBlockEvent(response, response != None))
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

        command = b'AT+SBDWB=' + str(len(msg)).encode('utf-8')
        self.s.write(command + b'\r')

        if self.serial_readline() == command:
            if self.serial_readline() == b'READY':
                checksum = 0
                for c in msg:
                    checksum += c
                self.s.write( msg )
                self.s.write( checksum >> 8 )
                self.s.write( checksum & 0xFF )
                self.serial_readline()   #BLANK
                result = False
                if self.serial_readline() == b'0':
                    result = True
                self.serial_readline()   #BLANK
                self.serial_readline()   #OK
                return result
        return False


    def _enableEcho(self):
        self._ensureConnectionStatus()
        self.send_command("ATE1")
        return not self.expect("OK") == None

    def _disableFlowControl(self):
        self._ensureConnectionStatus()
        self.send_command("AT&K0")
        return not self.expect("OK") == None

    def _disableRingAlerts(self):
        self._ensureConnectionStatus()
        self.send_command("AT+SBDMTA=0")
        return not self.expect("OK") == None

    def _attemptSession(self):
        self._ensureConnectionStatus()
        self.send_command("AT+SBDIX")
        # +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MTqueued>
        response = self.expect("+SBDIX: ")
        self.serial_readline()   #BLANK
        self.serial_readline()   #OK

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
                self._processMtMessage(mtMsn)

            self.callback.rockBlockRxMessageQueue(mtQueued)

            #There are additional MT messages to queued to download
            if mtQueued > 0 and self.autoSession == True:
                self._attemptSession() # TODO: get rid of recursion

            if moStatus <= 4:
                return True

        return False


    def _processMtMessage(self, mtMsn):
        self._ensureConnectionStatus()
        self.send_command("AT+SBDRB")
        response = self.serial_readline().decode('utf-8')
        #response = self.serial_readline().replace(b'AT+SBDRB\r',b'').strip()
        if response == "OK":
            self.callback.rockBlockRxReceived(mtMsn, "")
        else:
            content = response[2:-2]
            self.callback.rockBlockRxReceived(mtMsn, content)
            self.serial_readline()   #OK


    def _clearMoBuffer(self):
        self._ensureConnectionStatus()
        self.send_command("AT+SBDD0")
        r1 = self.expect("0")
        self.serial_readline()  #BLANK
        self.serial_readline()  #OK
        return not r1 == None
