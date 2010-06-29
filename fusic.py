#!/usr/bin/env python
"""LG Fusic Status

This small script makes use of the fact that the LG Fusic phone shows
up as a serial device when plugged on a Linux box.

You can adjust the COM_DEVICE constant below if your device is attached
to a different device file.

Copyright (c) 2010, Bertrand Janin

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

"""
import sys
import serial
import re

class FusicHandler(object):
    READ_BUFFER_SIZE = 128
    READ_TIMEOUT = 0.05
    COM_DEVICE = "/dev/ttyACM0"
    COM_SPEED = 115200
    BCS_CHAR = {
        0: "Battery Powered",
        1: "DC Powered, has battery",
        2: "DC Powered, no battery",
        3: "Power fault"
    }

    def init(self):
        self.port = None

    def send_cmd(self, cmd):
        self.port.write(cmd + "\r\n")
        response = ""
        buf = "0" * self.READ_BUFFER_SIZE
        while len(buf) == self.READ_BUFFER_SIZE:
            buf = self.port.read(self.READ_BUFFER_SIZE)
            response += buf
        return response

    def flush_buffer(self):
        """Read the port until buffer is empty."""
        buf = "0" * 128
        while len(buf) == 128:
            buf = self.port.read(128)

    def connect(self):
        """Connect and flush the buffer in case we have stalled commands."""
        try:
            self.port = serial.Serial(self.COM_DEVICE, self.COM_SPEED,
                    timeout=self.READ_TIMEOUT)
        except Exception, e:
            print("%s" % (e,))
            sys.exit(-1)
        self.flush_buffer()

    def _gmparse(self, keyword, s):
        """Given a response and a keyword, parse the value of an AT command."""
        gm_re = keyword + r":\s*([^\r\n]*)"
        matches = re.findall(gm_re, s)
        if not matches:
            return None
        return matches[0]

    def _getgmvar(self, var):
        res = self.send_cmd("AT+" + var)
        value = self._gmparse(var, res)
        if not value:
            return "N/A"
        return value

    def _linesplit(self, s):
        """Boldly strip and split a response per line breaks."""
        return re.split("[\r\n]+", s.strip())

    def _commasplit(self, s):
        """Split with commas and spaces."""
        return re.split(r"[,\s]+", s)

    def get_manufacturer(self):
        return self._getgmvar("GMI")

    def get_model(self):
        return self._getgmvar("GMM")

    def get_revision(self):
        return self._getgmvar("GMR")

    def get_sn(self):
        return self._getgmvar("GSN")

    def get_cap(self):
        s = self._getgmvar("GCAP")
        return self._commasplit(s)

    def get_raw_link_quality(self):
        """Retrieve the ``Received Signal Strength Indicator`` and
        ``Bit Error Ratio``.
        """
        res = self.send_cmd("AT+CSQ")
        ret = self._linesplit(res)
        if len(ret) != 3:
            return None
        rssi, ber = self._commasplit(ret[1])
        return int(rssi), int(ber)

    def get_link_quality(self):
        """Give an estimated link quality value in percent from the RSSI and
        BER."""
        rssi, ber = self.get_raw_link_quality()

        # A bit-error ratio above 90 almost guarantees a bad reception
        lq = float(rssi) * 1.0 / float(ber)

        return lq

    def get_battery(self):
        """Returns the ``Battery Charge Status`` and ``Battery Charge Level``,
        the bcs could be:
            * 0 MT is powered by the battery
            * 1 MT has a battery connected, but is not powered by it
            * 2 MT does not have a battery connected
            * 3 Recognized power fault, calls inhibited
        And ``bcl`` is between 1-100.
        """
        res = self.send_cmd("AT+CBC")
        ret = self._linesplit(res)
        if len(ret) != 3:
            return None
        bcs, bcl = re.split(r"[, ]+", ret[1])
        return int(bcs), int(bcl)

    def print_id(self):
        """Get Manufacturer, Model, etc..."""
        print("Manufacturer: " + self.get_manufacturer())
        print("Model: " + self.get_model())
        print("Revision: " + self.get_revision())
        print("Serial Number: " + self.get_sn())
        print("Capabilities: " + ", ".join(self.get_cap()))
        rssi, ber = self.get_raw_link_quality()
        lq = self.get_link_quality()
        print("Link Quality: %.2f%% (RSSI=%d BER=%d)" % (lq, rssi, ber))
        bcs, bcl = self.get_battery()
        print("Battery: %d%% (%s)" % (bcl, self.BCS_CHAR[bcs]))

    def hello(self):
        response = self.send_cmd("AT")
        if "OK" in response:
            return True
        else:
            return False

def c(cmd):
    """Easy function when debugging."""
    print(app.send_cmd(cmd))

if __name__ == '__main__':
    app = FusicHandler()
    app.connect()
    if not app.hello():
        sys.exit(-1)
    app.print_id()
