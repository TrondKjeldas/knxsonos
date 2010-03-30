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
from brisa.core.threaded_call import run_async_function

import eibclient.eibclient
from eibclient.common import *

import sys

class KnxListenGrpAddr():

    def __init__(self, url, gaddr, action):

        self.gaddr   = gaddr
        self.running = True


        # The action could be just one action, or a list of actions.
        # Convert the list to a list of just one, then it can alway
        # be handled as a list...
        if type(action) == type([]):
            self.action  = action
        else:
            self.action = [ action ]
        
        try:
            self.con = eibclient.eibclient.EIBSocketURL (url)
        except (Exception), e:
            print e

        dest = readgaddr (self.gaddr)
        if (eibclient.eibclient.EIBOpenT_Group (self.con, dest, 0) == -1):
            print "Connect failed"
            sys.exit(1);

    def stop(self):
        self.running = False
        
    def telegram_loop(self):

        #print "KNX: Entering read loop..."
        while self.running:
            try:
                (result,
                 buf, src) = eibclient.eibclient.EIBGetAPDU_Src (self.con)
                if len(buf) < 2:
                    print "Read failed"
                    sys.exit(1)
                if (ord(buf[0]) & 0x3 or (ord(buf[1]) & 0xc0) == 0xc0):
                    print"Unknown APDU from %s" % individual2string(src)
                    
                #print "RESULT: %s" %str(result)
                #print "SRC: %s" %str(src)
                #sys.stdout.write("BUF: ")
                #for b in buf:
                #    sys.stdout.write("0x%x " % ord(b))
                #sys.stdout.write("\n")

                print("KNX:  Group address %s"
                      " received from %s" %(self.gaddr, individual2string(src)))

                for a in self.action:
                    if callable(a):
                        a()
                    else:
                        print "KNX:  Can not call action: %s" %str(a)
            except (Exception), e:
                print e

        print "KNX:  Ending thread..."
        print "KNX:  Closing..."
        eibclient.EIBClose (self.con)
        
class KnxInterface():

    def __init__(self, url, action_table):

        self.gaddrs = [ KnxListenGrpAddr(url, g,a)
                        for g,a in action_table ]
            
        
    def start(self):

        for g in self.gaddrs:
            run_async_function(g.telegram_loop, ())

    def stop(self):

        for g in self.gaddrs:
            g.stop()
            
            
