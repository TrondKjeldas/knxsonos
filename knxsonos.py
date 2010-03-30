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

import xml.etree.ElementTree as ET

from time import sleep

import sys, os

import sonos
import knx


banner = """
KnxSonos Copyright (C) 2010 Trond Kjeldaas
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under certain conditions; For more details see the file named
'LICENSE' which should be included with the release.
"""


def loadConfig():

    # Check if config file were specified
    cfgname = False
    try:
        if os.access(sys.argv[sys.argv.index('-c')+1], os.R_OK):
            cfgname = sys.argv[sys.argv.index('-c')+1]
    except ValueError:
        # No config file, try default
        if os.access("knxsonos.config", os.R_OK):
            cfgname = "knxsonos.config"
            
    if not cfgname:
        print "ERROR: Failed to load configuration file."
        print "ERROR: Either specify one with the -c option, or make"
        print "ERROR: sure that a file named knxsonos.config exists."
        sys.exit(1)
        
    root = ET.parse(cfgname).getroot()

    # First load KNX related config
    knx = { "url" : root.find("knx").attrib["url"] }

    # Then load Sonos related config
    zones    = []
    cmd_maps = {}
    for zone in root.findall("zone"):
        Z = { "name" : zone.attrib["name"] }

        # Load macros first, so we can expand them immidiately
        # when loading command mappings
        macros = {}
        for macro in zone.findall("macro"):
            macros[macro.attrib["name"]] = []

            for action in macro.findall("action"):
                macros[macro.attrib["name"]].append(action.attrib["command"])

        # Using recursion makes it easier to handle nested macros...
        def maybeExpandMacro(cl):
            ret = []
            for c in cl:
                if c in macros.keys():
                    ret.extend(maybeExpandMacro(macros[c]))
                else:
                    ret.append(c)
            return ret


        # Then load command mappings...
        cmd_map = []
        for cmd in zone.findall("mapping"):
            # Possibly expand macros...
            command = maybeExpandMacro([cmd.attrib["command"]])

            #print "expanded command: %s" %str(command)

            cmd_map.append( ( cmd.attrib["groupAddress"],
                              command ) )

        Z["cmdMap"] = cmd_map

        zones.append( Z )

    
    return { "knx" : knx, "zones" : zones }


if __name__ == '__main__':

    # Print license and dislaimers...
    print banner

    # Load config
    cfg = loadConfig()

    # Create and start Sonos controls for each zone
    knx_cmd_map = []
    for zone in cfg["zones"]:
        c = sonos.SonosCtrl(zone["name"])
        c.start()
        # Map commands to actual methods, but use the command
        # name instead of a method if no method is found...
        for ga, cmds in zone["cmdMap"]:
            cmds2 = [ c.getCmdDict().get(oneCmd, oneCmd) for oneCmd in cmds ]

            knx_cmd_map.append((ga, cmds2))

    #print knx_cmd_map

    # Create and start KNX interface
    k = knx.KnxInterface(cfg["knx"]["url"], knx_cmd_map)
    k.start()

    # Run reactor...
    reactor.add_after_stop_func(c.stop)
    reactor.add_after_stop_func(k.stop)
    reactor.main()
    












