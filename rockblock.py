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

class RockBlockProtocol(object):

    #RAW OUTPUT
    def process_serial(self, text):pass

    #CONNECTION
    def rockBlockConnected(self):pass
    def rockBlockDisconnected(self):pass

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
        self.s = serial.Serial(self.portId, 19200, timeout=5)
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
            

    def serial_readline(self):
        text = self.s.readline().strip()
        if self.callback != None and callable(self.callback.process_serial):
            self.callback.process_serial(text.decode('utf-8'))
        return text

    def send_command(self, command):
        self.s.write(command.encode('utf-8') + b'\r')
        echo = self.serial_readline()

    def expect(self, expected):
        response = self.serial_readline().decode('utf-8')
        if response.find(expected) >= 0:
            return response.replace(expected, "")
        else:
            return None

    #Ensure that the connection is still alive
    def ping(self):
        self._ensureConnectionStatus()
        command = b"AT"
        self.s.write(command + b'\r')
        if self.serial_readline() == command:
            if self.serial_readline() == b'OK':
                return True
            else:
                raise RockBlockException("ping: OK not received")
        else:
            raise RockBlockException("ping: command echo not received")

        return False


    #Handy function to check if connection is still alive, callback based on result
    def check_connection(self):
        self.s.timeout = 5
        if self.ping():
            if self.callback != None and callable(self.callback.rockBlockConnected):
                self.callback.rockBlockConnected()
        else:
            if self.callback != None and callable(self.callback.rockBlockDisconnected):
                self.callback.rockBlockDisconnected()


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

    def messageCheck(self):
        self._ensureConnectionStatus()
        if self.callback != None and callable(self.callback.rockBlockRxStarted):
            self.callback.rockBlockRxStarted()
        if self.connectionOk() and self._attemptSession():
            return True
        else:
            if self.callback != None and callable(self.callback.rockBlockRxFailed):
                self.callback.rockBlockRxFailed()


    def networkTime(self):
        self._ensureConnectionStatus()
        self.send_command("AT-MSSTM")
        response = self.expect("-MSSTM: ")
        self.serial_readline()   #BLANK
        self.serial_readline()   #OK
        if not response == None and not "no network service" in response:
            utc = int(response, 16)
            utc = int((self.IRIDIUM_EPOCH + (utc * 90))/1000)
            return utc
        else:
            return 0


    def sendMessage(self, msg):
        self._ensureConnectionStatus()

        if self.callback != None and callable(self.callback.rockBlockTxStarted):
            self.callback.rockBlockTxStarted()

        if self._queueMessage(msg) and self.connectionOk():
            if self._attemptSession():
                self.callback.rockBlockTxSuccess()
                return True

        if self.callback != None and callable(self.callback.rockBlockTxFailed):
            self.callback.rockBlockTxFailed()

        return False


    def getSerialIdentifier(self):
        self._ensureConnectionStatus()
        self.send_command("AT+GSN")
        response = self.serial_readline().decode('utf-8')
        self.serial_readline()   #BLANK
        self.serial_readline()   #OK
        return response


    #One-time initial setup function (Disables Flow Control)
    #This only needs to be called once, as is stored in non-volitile memory

    #Make sure you DISCONNECT RockBLOCK from power for a few minutes after this command has been issued...
    def setup(self):
        self._ensureConnectionStatus()
        #Disable Flow Control
        command = b'AT&K0'
        self.s.write(command + b'\r')
        if self.serial_readline() == command and self.serial_readline() == b'OK':
            #Store Configuration into Profile0
            command = b'AT&W0'
            self.s.write(command + b'\r')

            if self.serial_readline() == command and self.serial_readline() == b'OK':
                #Use Profile0 as default
                command = b'AT&Y0'
                self.s.write(command + b'\r')
                if self.serial_readline() == command and self.serial_readline() == b'OK':
                    #Flush Memory
                    command = b'AT*F'
                    self.s.write(command + b'\r')
                    if self.serial_readline() == command and self.serial_readline() == b'OK':
                        #self.close()
                        return True
        return False


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


    #Private Methods - Don't call these directly!
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
        SESSION_ATTEMPTS = 1
        while(True):
            if SESSION_ATTEMPTS == 0:
                return False
            SESSION_ATTEMPTS = SESSION_ATTEMPTS - 1
            command = b'AT+SBDIX'
            self.s.write(command + b'\r')
            if self.serial_readline() == command:
                response = self.serial_readline()
                if response.find(b'+SBDIX:') >= 0:
                    self.serial_readline()   #BLANK
                    self.serial_readline()   #OK

                    response = response.replace(b'+SBDIX: ', b'')    #+SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MTqueued>
                    parts = response.split(b',')
                    moStatus = int(parts[0])
                    moMsn = int(parts[1])
                    mtStatus = int(parts[2])
                    mtMsn = int(parts[3])
                    mtLength = int(parts[4])
                    mtQueued = int(parts[5])

                    #Mobile Originated
                    if moStatus <= 4:
                        self._clearMoBuffer()
                        if self.callback != None and callable(self.callback.rockBlockTxSuccess):
                            self.callback.rockBlockTxSuccess( moMsn )
                        pass
                    else:
                        if self.callback != None and callable(self.callback.rockBlockTxFailed):
                            self.callback.rockBlockTxFailed()

                    if mtStatus == 1 and mtLength > 0: #SBD message successfully received from the GSS.
                        self._processMtMessage(mtMsn)

                    #AUTOGET NEXT MESSAGE
                    if self.callback != None and callable(self.callback.rockBlockRxMessageQueue):
                        self.callback.rockBlockRxMessageQueue(mtQueued)

                    #There are additional MT messages to queued to download
                    if mtQueued > 0 and self.autoSession == True:
                        self._attemptSession() # TODO: get rid of recursion

                    if moStatus <= 4:
                        return True

        return False


    def connectionOk(self):
        self._ensureConnectionStatus()

        #Check valid Network Time
        if not self._isNetworkTimeValid():
            if self.callback != None and callable(self.callback.rockBlockSignalFail):
                self.callback.rockBlockSignalFail()
            return False

        #Check signal strength
        signal = self.requestSignalStrength()

        self.callback.rockBlockSignalUpdate(signal)

        if self.callback != None and callable(self.callback.rockBlockSignalFail):
            self.callback.rockBlockSignalFail()
        return False

        if signal >= self.SIGNAL_THRESHOLD:
            if self.callback != None and callable(self.callback.rockBlockSignalPass):
                self.callback.rockBlockSignalPass()
            return True
        else:
            self.callback.rockBlockSignalFail()
            return False


    def _processMtMessage(self, mtMsn):
        self._ensureConnectionStatus()
        command = b'AT+SDBRB'
        self.s.write(command + b'\r')
        response = self.serial_readline().replace(b'AT+SBDRB\r',b'').strip()
        if response == b'OK':
            raise RockBlockException("Unexpectd modem response: no message content")
            if self.callback != None and callable(self.callback.rockBlockRxReceived):
                self.callback.rockBlockRxReceived(mtMsn, b'')
        else:
            content = response[2:-2]
            if self.callback != None and callable(self.callback.rockBlockRxReceived):
                self.callback.rockBlockRxReceived(mtMsn, content)
            self.serial_readline()   #BLANK?


    def _isNetworkTimeValid(self):
        self._ensureConnectionStatus()
        command = b'AT-MSSTM'
        self.s.write(command + b'\r')
        if self.serial_readline() == command:  #Echo
            response = self.serial_readline()
            if response.startswith(b'-MSSTM'):    #-MSSTM: a5cb42ad / no network service
                self.serial_readline()   #OK
                self.serial_readline()   #BLANK
                if len(response) == 16:
                    return True
        return False

    def _clearMoBuffer(self):
        self._ensureConnectionStatus()
        command = b'AT+SBDD0'
        self.s.write(command + b'\r')
        if self.serial_readline() == command:
            if self.serial_readline()  == b'0':
                self.serial_readline()  #BLANK
                if self.serial_readline() == b'OK':
                    return True

        return False

    def _ensureConnectionStatus(self):
        if self.s == None or self.s.isOpen() == False:
            raise RockBlockException("failed connection status")
