#
#     Simple proxy to be able to control the Sonos system
#     from the KNX bus. Requires a running eibd daemon.
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

from brisa.core.reactors import install_default_reactor
reactor = install_default_reactor()

from brisa.core.threaded_call import run_async_function

import sonos
import knx

from time import sleep

banner = """
KnxSonos Copyright (C) 2010 Trond Kjeldaas
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under certain conditions; For more details see the file named
'LICENSE' which should be included with the release.
"""

if __name__ == '__main__':

    # Print license and dislaimers...
    print banner
    
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
    












