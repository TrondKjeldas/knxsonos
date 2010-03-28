
from brisa.core.threaded_call import run_async_function

import eibclient.eibclient
from eibclient.common import *

import sys

class KnxListenGrpAddr():

    def __init__(self, gaddr, action):

        self.gaddr   = gaddr
        self.running = True
        self.action  = action
        
        try:
            self.con = eibclient.eibclient.EIBSocketURL ("local:/tmp/eib")
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

            (result, buf, src) = eibclient.eibclient.EIBGetAPDU_Src (self.con)
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
            
            self.action()

        print "KNX:  Ending thread..."
        print "KNX:  Closing..."
        eibclient.EIBClose (self.con)
        
class KnxInterface():

    def __init__(self, action_table):

        self.gaddrs = [ KnxListenGrpAddr(g,a)
                        for g,a in action_table ]
            
        
    def start(self):

        for g in self.gaddrs:
            run_async_function(g.telegram_loop, ())

    def stop(self):

        for g in self.gaddrs:
            g.stop()
            
            
