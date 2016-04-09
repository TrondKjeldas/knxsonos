#!/usr/bin/python
##
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
import xml.etree.ElementTree as ET

from time import sleep

import sys
import os
import logging

import sonos
import knx

# create logger
logger = logging.getLogger('knxsonos')

banner = """
KnxSonos Copyright (C) 2010 Trond Kjeldaas
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under certain conditions; For more details see the file named
'LICENSE' which should be included with the release.
"""


def loadCommand(cmd):
    # Optional command parameter...
    if "param" in cmd.attrib.keys():
        param = cmd.attrib["param"]
    else:
        param = None

    # Command itself
    command = cmd.attrib["command"]

    return command, param


def loadMacros(element):
    macros = {}
    for macro in element.findall("macro"):
        macros[macro.attrib["name"]] = []

        for action in macro.findall("action"):

            command, param = loadCommand(action)

            macros[macro.attrib["name"]].append((command, param))

    return macros

# Using recursion makes it easier to handle nested macros...


def maybeExpandMacro(macros, cl):
    ret = []
    for (c, p) in cl:
        if c in macros.keys():
            ret.extend(maybeExpandMacro(macros, macros[c]))
        else:
            ret.append((c, p))
    return ret


def loadCommands(macros, element):
    cmd_map = []
    for cmd in element.findall("mapping"):

        command, param = loadCommand(cmd)

        # Possibly expand macros...
        command = maybeExpandMacro(macros, [(command, param)])

        # logger.debug("expanded command: %s" %str(command))

        cmd_map.append((cmd.attrib["groupAddress"],
                        command))

    return cmd_map


def loadZoneConfig(global_macros, root, zone):

    Z = {"name": zone.attrib["name"]}

    # make local copy of global macros, as we dont want to
    # leak local macros into the global dict...
    macros = dict(global_macros)

    # Load macros first, so we can expand them immidiately
    # when loading command mappings
    macros.update(loadMacros(zone))

    # First load global command mappings
    Z["cmdMap"] = loadCommands(macros, root)

    # Then load per-zone command mappings...
    Z["cmdMap"].extend(loadCommands(macros, zone))

    return Z


def loadConfig():

    # Check if config file were specified
    cfgname = False
    try:
        if os.access(sys.argv[sys.argv.index('-c') + 1], os.R_OK):
            cfgname = sys.argv[sys.argv.index('-c') + 1]
    except ValueError:
        # No config file, try default
        if os.access("knxsonos.config", os.R_OK):
            cfgname = "knxsonos.config"

    if not cfgname:
        logger.error("ERROR: Failed to load configuration file.")
        logger.error("ERROR: Either specify one with the -c option, or make")
        logger.error("ERROR: sure that a file named knxsonos.config exists.")
        sys.exit(1)

    root = ET.parse(cfgname).getroot()

    # First load KNX related config
    knx = {"url": root.find("knx").attrib["url"]}

    # Then load Sonos related config
    zones = []
    cmd_maps = {}

    # First load "global" macros and commands...
    global_macros = loadMacros(root)

    # Then load "per zone" macros and commands...
    for zone in root.findall("zone"):
        Z = loadZoneConfig(global_macros, root, zone)
        zones.append(Z)

    return {"knx": knx, "zones": zones}


def main():
    """The main entry point to knxsonos.py.
    This is installed as the script entry point.
    """
    try:
        status = 0

        # Print license and dislaimers...
        logger.info(banner)

        # Load config
        cfg = loadConfig()

        # Create and start Sonos control
        knx_cmd_map = []

        c = sonos.SonosCtrl([zone["name"] for zone in cfg["zones"]])
        c.start()

        # Map commands to actual methods, but use the command
        # name instead of a method if no method is found...
        for zone in cfg["zones"]:
            for ga, cmds in zone["cmdMap"]:
                cmds2 = [(c.getCmdDict().get(oneCmd, oneCmd), param)
                         for oneCmd, param in cmds]
                knx_cmd_map.append((zone["name"], ga, cmds2))

        # Create and start KNX interface
        k = knx.KnxInterface(cfg["knx"]["url"], knx_cmd_map)
        k.start()

        # Run main loop...
        # (nothing to do, everything happens in other threads)
        while True:
            try:
                sleep(1)

            except KeyboardInterrupt:
                k.stop()
                c.stop()
                exit(0)
    except SystemExit as err:
        # The user called `sys.exit()`.  Exit with their argument, if any.
        if err.args:
            status = err.args[0]
        else:
            status = None
    return status

if __name__ == '__main__':

    main()
