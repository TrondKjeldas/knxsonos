#
# Simple proxy to be able to control the Sonos system
# from the KNX bus. Requires a running eibd daemon.
#

from brisa.core.reactors import install_default_reactor
reactor = install_default_reactor()

from brisa.core.threaded_call import run_async_function

import sonos
import knx

from time import sleep

if __name__ == '__main__':

    # Create and start Sonos interface
    c = sonos.SonosCtrl("Living Room")
    c.start()

    # Create and start KNX interface
    k = knx.KnxInterface([ ("3/7/0", c.play),
                           ("3/7/1", c.pause),
                           ("3/7/2", c.prev),
                           ("3/7/3", c.next),
                           ("3/7/4", c.volup),
                           ("3/7/5", c.voldown) ])
    k.start()

    # Run reactor...
    reactor.add_after_stop_func(c.stop)
    reactor.add_after_stop_func(k.stop)
    reactor.main()
    












