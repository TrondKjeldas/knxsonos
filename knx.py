
from brisa.core.threaded_call import run_async_function

import eibclient.eibclient
from eibclient.common import *

import sys

class KnxListenGrpAddr():

    def __init__(self, gaddr, action):

        self.running = True
        self.action  = action
        
        try:
            self.con = eibclient.eibclient.EIBSocketURL ("local:/tmp/eib")
        except (Exception), e:
            print e

        dest = readgaddr (gaddr)
        if (eibclient.eibclient.EIBOpenT_Group (self.con, dest, 0) == -1):
            print "Connect failed"
            sys.exit(1);

    def stop(self):
        self.running = False
        
    def telegram_loop(self):

        print "KNX: Entering read loop..."
        while self.running:

            (result, buf, src) = eibclient.eibclient.EIBGetAPDU_Src (self.con)
            if len(buf) < 2:
                print "Read failed"
                sys.exit(1)
            if (ord(buf[0]) & 0x3 or (ord(buf[1]) & 0xc0) == 0xc0):
                print"Unknown APDU from %s" % individual2string(src)

            print "RESULT: %s" %str(result)
            print "SRC: %s" %str(src)
            sys.stdout.write("BUF: ")
            for b in buf:
                sys.stdout.write("0x%x " % ord(b))
            sys.stdout.write("\n")
            
            ps = ""
            if (ord(buf[1]) & 0xC0) == 0:
                ps = ps + "Read"
            elif (ord(buf[1]) & 0xC0) == 0x40:
                ps = ps + "Response"
            elif (ord(buf[1]) & 0xC0) == 0x80:
                ps = ps + "Write"
            else:
                ps = ps + "???"
	    
            ps = ps + " from "
            ps = ps + individual2string (src);
            if (ord(buf[1]) & 0xC0):	
                ps = ps + ": "
                if result == 2:
                    ps = ps + ( "%02X" % (ord(buf[1]) & 0x3F) )
                elif result == 3:
                    ps = ps + ( "%02X %02X" % (ord(buf[1]) & 0x3F,
                                               ord(buf[2])) )
                elif result == 4:
                    ps = ps + ( "%02X %02X %02X" % (ord(buf[1]) & 0x3F,
                                                    ord(buf[2]),
                                                    ord(buf[3])) )
                elif result == 5:
                    ps = ps + ( "%02X %02X %02X %02X" % (ord(buf[1]) & 0x3F,
                                                         ord(buf[2]),
                                                         ord(buf[3]),
                                                         ord(buf[4])) )
                else:
                    printHex (len - 2, buf + 2);
                    
            print ps;

            self.action()

        print "KNX: Ending thread..."
        print "KNX: Closing..."
        eibclient.EIBClose (self.con)
        
class KnxInterface():

    def __init__(self, ctrl):

        self.ctrl    = ctrl

        group_addresses = [ ("3/7/0", ctrl.play),
                            ("3/7/1", ctrl.pause),
                            ("3/7/2", ctrl.prev),
                            ("3/7/3", ctrl.next),
                            ("3/7/4", ctrl.volup),
                            ("3/7/5", ctrl.voldown) ]

        self.gaddrs = [ KnxListenGrpAddr(g,a)
                        for g,a in group_addresses ]
            
        
    def start(self):

        for g in self.gaddrs:
            run_async_function(g.telegram_loop, ())

    def stop(self):

        for g in self.gaddrs:
            g.stop()
            
            
