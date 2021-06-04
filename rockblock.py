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

    STATUS_INFO = 0
    STATUS_SUCCESS = 1
    STATUS_ERROR = 2

    # RAW OUTPUT
    def process_serial(self, text): pass

    # STATUS
    def status(self, message, status): pass

    # CONNECTION
    def rockBlockConnected(self): pass
    def rockBlockDisconnected(self): pass

    # NETWORK TIME
    def rockBlockNetworkTime(self, event): pass

    # IMEI
    def imei_event(self, event): pass

    # SIGNAL
    def signal_event(self, event): pass

    # SESSION
    def rockBlockSession(self, mo_status, mo_msn, mt_status,
                         mt_msn, mt_length, mt_queued): pass

    # MT
    def rockBlockRxStarted(self): pass
    def rockBlockRxFailed(self): pass
    def rockBlockRxReceived(self, mtmsn, data): pass
    def rockBlockRxMessageQueue(self, count): pass

    # MO
    def rockBlockTxStarted(self): pass
    def rockBlockTxFailed(self): pass
    def rockBlockTxSuccess(self, momsn): pass


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
    # May 11, 2014, at 14:23:55 (This will be 're-epoched' every couple of
    # years!)

    def __init__(self, portId, callback):
        self.s = None
        self.portId = portId
        self.callback = callback
        # When True, we'll automatically initiate additional sessions if more
        # messages to download
        self.autoSession = True
        self.SIGNAL_THRESHOLD = 2

        # try:
        self.s = serial.Serial(self.portId, 19200, timeout=5)
        if not (self._disableEcho()
                and self._disableFlowControl
                and self._disableRingAlerts()):
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
        try:
        text = self.s.readline().strip()
        self.callback.process_serial(text.decode('utf-8'))
        except OSError as e:
            raise RockBlockSerialException(msg=e.strerror)
        return text

    ##
    # Parsing
    ##

    def send_command(self, command):
        try:
        self.s.write(command.encode('utf-8') + b'\r')
        self.callback.process_serial(command)
        except OSError as e:
            raise RockBlockSerialException(msg=e.strerror)

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
        self.callback.status("Message RX started...",
                             RockBlockProtocol.STATUS_INFO)
        if self.connectionOk():
            # TODO: check for ring alert before attempting session
            self._perform_session()

    def sendMessage(self, msg):
        self.callback.status("Message TX started...",
                             RockBlockProtocol.STATUS_INFO)
        #if not self.connectionOk():
        #    return False

        if not self._queueMessage(msg):
            self.callback.status("queue message failed",
                                 RockBlockProtocol.STATUS_ERROR)
            return False

        return True
#        return self._perform_session()

    def connectionOk(self):
        self._verify_serial_connected()

        # Check valid Network Time
        if not self._isNetworkTimeValid():
            self.callback.status("Invalid network time",
                                 RockBlockProtocol.STATUS_ERROR)
            return False

        # Check signal strength
        # signal = self.requestSignalStrength()
        # if not signal > 0:
        #     self.callback.status("no signal", RockBlockProtocol.STATUS_ERROR)
        #     return False
        # else:
        #     return True
            return True

    def _isNetworkTimeValid(self):
        return self.networkTime() != 0

    def _verify_serial_connected(self):
        if self.s == None or self.s.isOpen() == False:
            raise RockBlockException("failed connection status")

    # One-time initial setup function (Disables Flow Control)
    # This only needs to be called once, as is stored in non-volitile memory
    #
    # Make sure you DISCONNECT RockBLOCK from power for a few minutes after
    # this command has been issued...
    def setup(self):
        self._verify_serial_connected()
        # Disable Flow Control
        self.send_command("AT&K0")
        self.expect("OK")

        # Store Configuration into Profile0
        self.send_command("AT&W0")
        self.expect("OK")

        # Use Profile0 as default
        self.send_command("AT&Y0")
        self.expect("OK")

        # Flush Memory
        self.send_command("AT*F")
        self.expect("OK")
        return True

    ##
    # AT Command Primitives
    ##

    def ping(self):
        self._verify_serial_connected()
        self.send_command("AT")
        response = self.expect("OK")

        return response != None

    # TODO: update signal status from here
    def requestSignalStrength(self):
        self._verify_serial_connected()
        self.send_command("AT+CSQ")
        self.serial_readline()
        response = self.expect("+CSQ:")
        self.expect("OK")
        try:
            signal = int(response)
        except:
            signal = 0
        self.callback.rockBlockSignalUpdate(signal)
#        ev = RockBlockEvent(signal, signal > 0)
#        self.callback.signal_event(ev)
        return signal

    def networkTime(self):
        self._verify_serial_connected()
        self.send_command("AT-MSSTM")
        response = self.expect("-MSSTM: ")
        self.expect("OK")  # OK
        utc = 0
        if response == None:
            self.callback.status("no network time response",
                                 RockBlockProtocol.STATUS_ERROR)
        elif "no network service" in response:
            self.callback.status("no network service",
                                 RockBlockProtocol.STATUS_ERROR)
        else:
            self.callback.status("network time success",
                                 RockBlockProtocol.STATUS_SUCCESS)
            utc = int(response, 16)
            utc = int((self.IRIDIUM_EPOCH + (utc * 90))/1000)
            self.callback.rockBlockNetworkTime(RockBlockEvent(utc, True))
        return utc

    def getSerialIdentifier(self):
        self._verify_serial_connected()
        self.send_command("AT+GSN")
        self.serial_readline()
        response = self.serial_readline().decode('utf-8')
        self.expect("OK")
        self.callback.imei_event(RockBlockEvent(response, response != None))
        return response

    def checkStatus(self):
        self._verify_serial_connected()
        self.requestSignalStrength()
        self.send_command("AT+SBDSX")
        response = self.expect("+SBDSX: ")
        self.expect("OK")
        if response != None:
            # 0 <MO flag>, 1 <MOMSN>, 2 <MT flag>, 3 <MTMSN>, 4 <RA flag>, 5 <msg waiting>
            # 0, 6, 0, -1, 0, 0
            mo_flag, mo_msn, mt_flag, mt_msn, ring_alert, msg_wait = response.split(", ")
            self.callback.status("Status: moflg={} mtflg={} ring={} msg wait={}".format(
                mo_flag, mt_flag, ring_alert, msg_wait), RockBlockProtocol.STATUS_INFO)
            if mt_flag == '1':
                self._read_mt_message()
            if ring_alert == '1' or mo_flag == '1':
                self._perform_session()
        return

    def _queueMessage(self, msg):
        self._verify_serial_connected()

        if len(msg) > 340:
            self.callback.status(
                "message must be 340 bytes or less", RockBlockProtocol.STATUS_ERROR)
            return False

        self.callback.status("adding message to buffer",
                             RockBlockProtocol.STATUS_INFO)
        self.send_command("AT+SBDWB={:d}".format(len(msg)))
        if self.expect("READY") != None:
            checksum = 0
            for c in msg:
                checksum += c
            checksum &= 0xFFFF
            self.s.write(msg)
            self.s.write(bytes([checksum >> 8]))
            self.s.write(bytes([checksum & 0xFF]))
            response = self.expect("0")
            self.serial_readline()  # BLANK
            self.serial_readline()  # OK
            if response == None:
                self.callback.status(
                    "checksum error", RockBlockProtocol.STATUS_ERROR)
                return False
            else:
                self.callback.status(
                    "message queued", RockBlockProtocol.STATUS_SUCCESS)
            return True
        else:
            self.callback.status("READY message not found",
                                 RockBlockProtocol.STATUS_ERROR)
            return False

    def _perform_session(self):
        self._verify_serial_connected()

        self.callback.status("session started", RockBlockProtocol.STATUS_INFO)

        self.send_command("AT+SBDIX")
        # +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MTqueued>
        response = self.expect("+SBDIX: ")
        self.expect("OK")

        if response == None:
            self.callback.status("invalid session response",
                                 RockBlockProtocol.STATUS_ERROR)
            return False

        parts = response.split(",")
        moStatus = int(parts[0])
        moMsn = int(parts[1])
        mtStatus = int(parts[2])
        mtMsn = int(parts[3])
        mtLength = int(parts[4])
        mtQueued = int(parts[5])

        self.callback.rockBlockSession(
            moStatus, moMsn, mtStatus, mtMsn, mtLength, mtQueued)

        # Mobile Originated
        if moStatus <= 4:
            self._clearMoBuffer()

        if mtStatus == 1 and mtLength > 0:
            # SBD message successfully received from the GSS.
            msg = self._read_mt_message()
            self.callback.rockBlockRxReceived(mtMsn, msg)
        # TODO: handle mtStatus error values

        if moStatus <= 4:
            self.callback.status("session succeeded",
                                 RockBlockProtocol.STATUS_SUCCESS)
            return True
        else:
            self.callback.status(
                "session failed", RockBlockProtocol.STATUS_ERROR)
            return False

    def _read_mt_message(self):
        self._verify_serial_connected()

        self.callback.status("Reading MT message",
                             RockBlockProtocol.STATUS_INFO)

        self.send_command("AT+SBDRB")
        length = int.from_bytes(self.s.read(2), byteorder='big')
        msg = ""
        if length > 0:
            msg = self.s.read(length)
            # compute checksum
            mysum = 0
            for c in msg:
                mysum += c
            mysum &= 0xffff

        cksum = int.from_bytes(self.s.read(2), byteorder='big')

        self.expect("OK")

        if length > 0:
            # compare checksum
            if mysum != cksum:
                self.callback.status("checksum mismatch {:d} {:d}".format(
                    mysum, cksum), RockBlockProtocol.STATUS_ERROR)
            self._clearMtBuffer()
            return msg.decode('utf-8')

        return None

    def _clearMoBuffer(self):
        self._verify_serial_connected()
        self.callback.status("clearing MO buffer",
                             RockBlockProtocol.STATUS_INFO)
        self.send_command("AT+SBDD0")
        r1 = self.expect("0")
        self.serial_readline()  # BLANK
        self.serial_readline()  # OK
        if r1 == None:
            self.callback.status("clear buffer: {} expected 0".format(
                r1), RockBlockProtocol.STATUS_ERROR)
            return False
        else:
            return True

    def _clearMtBuffer(self):
        self._verify_serial_connected()
        self.callback.status("clearing MT buffer",
                             RockBlockProtocol.STATUS_INFO)
        self.send_command("AT+SBDD1")
        r1 = self.expect("0")
        self.serial_readline()  # BLANK
        self.serial_readline()  # OK
        if r1 == None:
            self.callback.status("clear buffer: {} expected 0".format(
                r1), RockBlockProtocol.STATUS_ERROR)
            return False
        else:
            return True

    def _enableEcho(self):
        self._verify_serial_connected()
        self.send_command("ATE1")
        return not self.expect("OK") == None

    def _disableEcho(self):
        self._verify_serial_connected()
        self.send_command("ATE0")
        self.serial_readline()
        return not self.expect("OK") == None

    def _disableFlowControl(self):
        self._verify_serial_connected()
        self.send_command("AT&K0")
        return not self.expect("OK") == None

    def _disableRingAlerts(self):
        self._verify_serial_connected()
        self.send_command("AT+SBDMTA=0")
        return not self.expect("OK") == None
