#
#     Copyright 2010 Trond Kjeldaas
#
#     This file is part of KnxSonos
#
#     KnxSonos is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     KnxSonos is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
from EIBConnection import EIBConnection, EIBBuffer, EIBAddr
from EIBConnection import individual2string, readgaddr

from sys import argv, exit
from threading import Thread


class KnxListenGrpAddr(Thread):

    def __init__(self, url, zone_name, gaddr, action):

        # Call base class constructor first...
        Thread.__init__(self)

        self.name = "%s_%s" % (zone_name.encode("utf-8"), gaddr)
        self.zone_name = zone_name
        self.gaddr = gaddr
        self.stopping = False

        # To make sure the thread exit when the main program terminates...
        self.daemon = True

        # The action could be just one action, or a list of actions.
        # Convert the list to a list of just one, then it can alway
        # be handled as a list...
        if type(action) == type([]):
            self.action = action
        else:
            self.action = [action]

        try:
            self.con = EIBConnection()
        except:
            print "Could not instanciate EIBConnection"
            exit(1)

        if self.con.EIBSocketURL(url) != 0:
            print "Could not connect to: %s" % url
            exit(1)

        dest = readgaddr(self.gaddr)
        if (self.con.EIBOpenT_Group(dest, 0) == -1):
            print "Connect failed"
            exit(1)

    def stop(self):

        self.stopping = True
        self.join(0.1)

        if self.isAlive():
            print "Thread %s did not stop!" % self.name

    def run(self):

        # print "KNX: Entering read loop..."
        while not self.stopping:
            try:
                src = EIBAddr()
                buf = EIBBuffer()
                length = self.con.EIBGetAPDU_Src(buf, src)
                if length < 2:
                    print "Read failed"
                    exit(1)
                if ((buf.buffer[0] & 0x3) or (buf.buffer[1] & 0xc0) == 0xc0):
                    print"Unknown APDU from %s" % individual2string(src.data)

                # print "LENGTH: %s" %str(length)
                # print "SRC: %s" %str(src.data)
                #sys.stdout.write("BUF: ")
                # for b in buf.buffer:
                #    sys.stdout.write("0x%x " % b)
                # sys.stdout.write("\n")
                print("KNX:  Group address %s"
                      " received from %s" % (self.gaddr,
                                             individual2string(src.data)))

                for (a, p) in self.action:
                    if callable(a):
                        if p == None:
                            a(self.zone_name)
                        else:
                            a(self.zone_name, p)
                    else:
                        print "KNX:  Can not call action: %s" % str(a)
            except (Exception), e:
                print e

        print "KNX:  Ending thread..."
        print "KNX:  Closing..."
        self.con.EIBClose()


class KnxInterface():

    def __init__(self, url, action_table):

        self.gaddrs = [KnxListenGrpAddr(url, zn, g, a)
                       for zn, g, a in action_table]

    def start(self):

        for g in self.gaddrs:
            g.start()

    def stop(self):

        for g in self.gaddrs:
            g.stop()
