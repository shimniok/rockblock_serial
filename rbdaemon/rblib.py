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

import serial


class RockBlockEventHandler(object):
    STATUS_INFO = 0
    STATUS_SUCCESS = 1
    STATUS_ERROR = 2

    # RAW OUTPUT
    def on_serial(self, text): pass

    # STATUS
    def on_status(self, message, status): pass


class RockBlockException(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "RockBlock General Error"
        super(RockBlockException, self).__init__(msg)


class RockBlockSerialException(RockBlockException):
    def __init__(self, msg=None):
        if msg is None:
            msg = "RockBlock Serial Error"
        super(RockBlockSerialException, self).__init__(msg)


class RockBlockPortException(RockBlockException):
    def __init__(self, msg=None):
        if msg is None:
            msg = "RockBlock Port Config Error"
        super(RockBlockPortException, self).__init__(msg)


class RockBlockStatus(object):
    ''' Represents Rockblock status (from SBDSX) '''

    def __init__(self, mo_flag=0, mo_msn=-1, mt_flag=0, mt_msn=-1, ring=0, waiting=0):
        self.mo_flag = mo_flag
        self.mo_msn = mo_msn
        self.mt_flag = mt_flag
        self.mt_msn = mt_msn
        self.ring = ring
        self.waiting = waiting

    def toJSON(self):
        json = {
            "mo_flag": self.mo_flag,
            "mo_msn": self.mo_msn,
            "mt_flag": self.mt_flag,
            "mt_msn": self.mt_msn,
            "ring": self.ring,
            "waiting": self.waiting
        }
        return json

class RockBlockSessionStatus(object):
    ''' Represents the status of a RockBlock session '''

    def __init__(self, mo_status, mo_msn, mt_status, mt_msn, mt_length, mt_queued):
        self.mo_status = mo_status
        self.mo_msn = mo_msn
        self.mt_status = mt_status
        self.mt_msn = mt_msn
        self.mt_length = mt_length
        self.mt_queued = mt_queued


class RockBlock(object):
    IRIDIUM_EPOCH = 1399818235000
    # May 11, 2014, at 14:23:55 (This will be 're-epoched' every couple of
    # years!)

    def __init__(self, portId, callback):
        self.s = None
        self.portId = portId
        self.callback = callback

        # try:
        self.s = serial.Serial(self.portId, 19200, timeout=5)
        if not (self.disable_echo() and self.disable_flow_control and self.disable_ring_alerts()):
            self.close_serial()
            raise RockBlockPortException

    ##
    # Serial Specific
    ##

    def close_serial(self):
        if self.s and self.s.is_open:
            self.s.close()
            self.s = None


    def serial_readline(self):
        try:
            text = self.s.readline().strip()
            self.callback.on_serial(text.decode('utf-8'))
        except OSError as e:
            raise RockBlockSerialException(msg=e.strerror)
        return text

    ##
    # Parsing
    ##

    def send_command(self, command):
        try:
            self.s.write(command.encode('utf-8') + b'\r')
            self.callback.on_serial(command)
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

    # def messageCheck(self):
    #     self.callback.status("Message RX started...",
    #                          RockBlockProtocol.STATUS_INFO)
    #     if self.connectionOk():
    #         # TODO: check for ring alert before attempting session
    #         self.perform_session()

    def sendMessage(self, msg):
        self.callback.status("Message TX started...",
                             RockBlockEventHandler.STATUS_INFO)
        # if not self.connectionOk():
        #    return False

        if not self.write_mo_buffer(msg):
            self.callback.status("queue message failed",
                                 RockBlockEventHandler.STATUS_ERROR)
            return False

        return True
#        return self._perform_session()

    def connectionOk(self):
        self._verify_serial_connected()

        # Check valid Network Time
        if not self._isNetworkTimeValid():
            self.callback.status("Invalid network time",
                                 RockBlockEventHandler.STATUS_ERROR)
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
        return self.get_net_time() != 0

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

    # def ping(self):
    #     self._verify_serial_connected()
    #     self.send_command("AT")
    #     response = self.expect("OK")

    #     return response != None

    # TODO: update signal status from here
    def get_signal_strength(self):
        self._verify_serial_connected()
        self.send_command("AT+CSQ")
        response = self.expect("+CSQ:")
        self.expect("OK")
        try:
            signal = int(response)
        except:
            signal = 0
        return signal

    def get_net_time(self):
        self._verify_serial_connected()
        self.send_command("AT-MSSTM")
        response = self.expect("-MSSTM: ")
        self.expect("OK")  # OK
        utc = 0
        if response == None:
            self.callback.status("no network time response",
                                 RockBlockEventHandler.STATUS_ERROR)
        elif "no network service" in response:
            self.callback.status("no network service",
                                 RockBlockEventHandler.STATUS_ERROR)
        else:
            self.callback.status("network time success",
                                 RockBlockEventHandler.STATUS_SUCCESS)
            utc = int(response, 16)
            utc = int((self.IRIDIUM_EPOCH + (utc * 90))/1000)
            # self.callback.rockBlockNetworkTime(RockBlockEvent(utc, True))
        return utc

    def get_imei(self):
        self._verify_serial_connected()
        self.send_command("AT+GSN")
        self.serial_readline()
        response = self.serial_readline().decode('utf-8')
        self.expect("OK")
        # self.callback.imei_event(RockBlockEvent(response, response != None))
        return response

    def get_status(self):
        self._verify_serial_connected()
        # self.get_signal_strength()
        self.send_command("AT+SBDSX")
        response = self.expect("+SBDSX: ")
        self.expect("OK")
        if response != None:
            # 0 <MO flag>, 1 <MOMSN>, 2 <MT flag>, 3 <MTMSN>, 4 <RA flag>, 5 <msg waiting>
            # 0, 6, 0, -1, 0, 0
            mo_fl, mo_msn, mt_fl, mt_msn, ring, msg_w = response.split(", ")
            #print("mo_msn={} mt_msn={} msg_wait={}".format(mo_msn, mt_msn, msg_w))
            return RockBlockStatus(mo_flag=int(mo_fl),
                                   mo_msn=int(mo_msn),
                                   mt_flag=int(mt_fl),
                                   mt_msn=int(mt_msn),
                                   ring=int(ring),
                                   waiting=int(msg_w))
        else:
            return RockBlockStatus()

    def write_mo_buffer(self, msg):
        self._verify_serial_connected()

        if len(msg) > 340:
            self.callback.status(
                "message must be 340 bytes or less", RockBlockEventHandler.STATUS_ERROR)
            return False

        self.callback.status("adding message to buffer",
                             RockBlockEventHandler.STATUS_INFO)
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
                    "checksum error", RockBlockEventHandler.STATUS_ERROR)
                return False
            else:
                self.callback.status(
                    "message queued", RockBlockEventHandler.STATUS_SUCCESS)
            return True
        else:
            self.callback.status("READY message not found",
                                 RockBlockEventHandler.STATUS_ERROR)
            return False

    def perform_session(self):
        self._verify_serial_connected()

        self.callback.status("session started", RockBlockEventHandler.STATUS_INFO)

        self.send_command("AT+SBDIX")
        # +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MTqueued>
        response = self.expect("+SBDIX: ")
        self.expect("OK")

        if response == None:
            self.callback.status("invalid session response",
                                 RockBlockEventHandler.STATUS_ERROR)
            return False

        mo_status, mo_msn, mt_status, mt_msn, mt_length, mt_queued = response.split(
            ",")

        return RockBlockSessionStatus(
            int(mo_status),
            int(mo_msn),
            int(mt_status),
            int(mt_msn),
            int(mt_length),
            int(mt_queued))

        # mo_status = int(parts[0])
        # mo_msn = int(parts[1])
        # mt_status = int(parts[2])
        # mt_msn = int(parts[3])
        # mt_length = int(parts[4])
        # mt_queued = int(parts[5])

        # self.callback.rockBlockSession(
        #     mo_status, mo_msn, mt_status, mt_msn, mt_length, mt_queued)

        # # Mobile Originated
        # if mo_status <= 4:
        #     self.clear_mo_buffer()

        # if mt_status == 1 and mt_length > 0:
        #     # SBD message successfully received from the GSS.
        #     msg = self.read_mt_buffer()
        #     self.callback.rockBlockRxReceived(mt_msn, msg)
        # # TODO: handle mtStatus error values

        # if mo_status <= 4:
        #     self.callback.status("session succeeded",
        #                          RockBlockProtocol.STATUS_SUCCESS)
        #     return True
        # else:
        #     self.callback.status(
        #         "session failed: ".format(self.mo_status_to_string(mo_status)), RockBlockProtocol.STATUS_ERROR)
        #     return False

    def read_mt_buffer(self):
        self._verify_serial_connected()

        self.callback.status("Reading MT message",
                             RockBlockEventHandler.STATUS_INFO)

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
                    mysum, cksum), RockBlockEventHandler.STATUS_ERROR)
            self.clear_mt_buffer()
            return msg.decode('utf-8')

        return None

    def clear_mo_buffer(self):
        self._verify_serial_connected()
        self.callback.status("clearing MO buffer",
                             RockBlockEventHandler.STATUS_INFO)
        self.send_command("AT+SBDD0")
        r1 = self.expect("0")
        self.serial_readline()  # BLANK
        self.serial_readline()  # OK
        if r1 == None:
            self.callback.status("clear buffer: {} expected 0".format(
                r1), RockBlockEventHandler.STATUS_ERROR)
            return False
        else:
            return True

    def clear_mt_buffer(self):
        self._verify_serial_connected()
        self.callback.status("clearing MT buffer",
                             RockBlockEventHandler.STATUS_INFO)
        self.send_command("AT+SBDD1")
        r1 = self.expect("0")
        self.serial_readline()  # BLANK
        self.serial_readline()  # OK
        if r1 == None:
            self.callback.status("clear buffer: {} expected 0".format(
                r1), RockBlockEventHandler.STATUS_ERROR)
            return False
        else:
            return True

    def enable_echo(self):
        self._verify_serial_connected()
        self.send_command("ATE1")
        return not self.expect("OK") == None

    def disable_echo(self):
        self._verify_serial_connected()
        self.send_command("ATE0")
        self.serial_readline()
        return not self.expect("OK") == None

    def disable_flow_control(self):
        self._verify_serial_connected()
        self.send_command("AT&K0")
        return not self.expect("OK") == None

    def disable_ring_alerts(self):
        self._verify_serial_connected()
        self.send_command("AT+SBDMTA=0")
        return not self.expect("OK") == None

    """
    0 MO message, if any, transferred successfully.
    1 MO message, if any, transferred successfully, but the MT message in the queue was too big to be transferred.
    2 MO message, if any, transferred successfully, but the requested Location Update was not accepted.
    3..4 Reserved, but indicate MO session success if used. 5..8 Reserved, but indicate MO session failure if used.
    10 GSS reported that the call did not complete in the allowed time.
    11 MO message queue at the GSS is full.
    12 MO message has too many segments.
    13 GSS reported that the session did not complete.
    14 Invalid segment size.
    15 Access is denied.
    ISU-reported values:
    16 ISU has been locked and may not make SBD calls (see +CULK command).
    17 Gateway not responding (local session timeout).
    18 Connection lost (RF drop).
    19 Link failure (A protocol error caused termination of the call).
    20..31 Reserved, but indicate failure if used.
    32 No network service, unable to initiate call.
    33 Antenna fault, unable to initiate call.
    34 Radio is disabled, unable to initiate call (see *Rn command).
    35 ISU is busy, unable to initiate call.
    36 Try later, must wait 3 minutes since last registration.
    37 SBD service is temporarily disabled.
    38 Try later, traffic management period (see +SBDLOE command)
    39..63 Reserved, but indicate failure if used.
    64 Band violation (attempt to transmit outside permitted frequency band).
    65 PLL lock failure; hardware error during attempted transmit.
    """

    mo_status_codes = {
        "0": "MO message transferred.",
        "1": "MO message transferred. MT message in queue too big.",
        "2": "MO message transferred. Location update rejected.",
        "10": "GSS: call did not complete in time.",
        "11": "GSS: MO message queue full.",
        "12": "MO message has too many segments.",
        "13": "GSS: session did not complete.",
        "14": "Invalid segment size.",
        "15": "Access is denied.",
        "16": "ISU locked, (see AT+CULK command).",
        "17": "Gateway not responding (local session timeout).",
        "18": "Connection lost (RF drop).",
        "19": "Link failure (A protocol error caused termination of the call).",
        "32": "No network service, unable to initiate call.",
        "33": "Antenna fault, unable to initiate call.",
        "34": "Radio is disabled, unable to initiate call (see AT*Rn command)",
        "35": "ISU is busy, unable to initiate call.",
        "36": "Try later, must wait 3 minutes since last registration.",
        "37": "SBD service is temporarily disabled.",
        "38": "Try later, traffic management period (see +SBDLOE command).",
        "64": "Band violation (attempt to transmit outside permitted frequency band).",
        "65": "PLL lock failure; hardware error during attempted transmit."
    }

    def mo_status_to_string(self, err):
        try:
            message = self.mo_status_codes.get("{}".format(err))
            return message
        except Exception as ex:
            self.callback.status("key error {}".format(
                ex), RockBlockEventHandler.STATUS_ERROR)
        return None
