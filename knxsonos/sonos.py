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
from soco import discover
from time import sleep
from threading import Thread, Lock
import logging

#
#
# To join group: SetAvTransportURI,
#                current URI ==x-rincon:RINCON_000E58334AF601400
#
# To leave group: BecomeCoordinatorOfStandaloneGroup
#
#


#
# Just a wrapper class for the SoCo controller class...
#
class SonosCtrl():

    def __init__(self, zone_names):

        self.logger = logging.getLogger('knxsonos')

        self.zones = {}
        self.needed_zones = zone_names
        self.quit = False
        self.zlock = Lock()

    def getCmdDict(self):
        """Return a dictionary that can be used to map commans to methods"""

        return {"play": self.play,
                "pause": self.pause,
                "next": self.next,
                "previous": self.prev,
                "volume+": self.volumeUp,
                "volume-": self.volumeDown,
                "volumeSet": self.volumeSet,
                "setURI": self.setURI}

    def start(self):
        self.logger.info("Starting.")
        self.quit = False

        self.t = Thread(target=self.discoverer, name="knxsonos discoverer")
        self.t.start()

    def stop(self):
        self.logger.info("Stopping.")
        self.quit = True
        self.t.join()
        self.logger.info("Stopped")

    def discoverer(self):

        def addOrReplaceZone(zone):

            if zone.player_name in self.zones:
                if zone.ip_address != self.zones[zone.player_name].ip_address:
                    with self.zlock:
                        self.zones.pop(zone.player_name)
                    self.logger.debug("Replacing: %s"%zone.player_name)
                else:
                    self.logger.debug("Unchanged: %s"%zone.player_name)
                    return
            else:
                self.logger.info("Adding: %s"%zone.player_name)

            with self.zlock:
                self.zones[zone.player_name] = zone

        def removeZone(zone_name):
            if zone_name in self.zones:
                with self.zlock:
                    self.zones.pop(zone_name)
                self.logger.info("Expiring: %s"%zone_name)

        while not self.quit:

            zones_needed = list(self.needed_zones)
            self.logger.debug("Need to find these zones: %s" %zones_needed)

            zones_discovered = discover(10)

            for z in list(zones_discovered):

                addOrReplaceZone(z)

                try:
                    zones_needed.remove(z.player_name)
                except ValueError:
                    self.logger.debug("Did not want: %s" %z.player_name)

            for z in zones_needed:
                removeZone(z)

            if len(zones_needed) > 0:
                self.logger.warning("Missing zones: %s" % zones_needed)
                self.logger.warning("New attempt in 5 sec...")
                for x in range(0,5):
                    if self.quit:
                        break
                    sleep(1)
            else:
                self.logger.debug("Found all needed zones: %s" %self.zones.keys())
                self.logger.debug("New check in 60 sec...")
                for x in range(0,60):
                    if self.quit:
                        break
                    sleep(1)

    #
    # Sonos commands
    #

    def pause(self, zn):
        if zn in self.zones:
            self.zones[zn].group.coordinator.pause()
        else:
            self.logger.warning("Zone %s not discovered" %zn)

    def play(self, zn):
        if zn in self.zones:
            self.zones[zn].group.coordinator.play()
        else:
            self.logger.warning("Zone %s not discovered" %zn)

    def next(self, zn):
        if zn in self.zones:
            self.zones[zn].group.coordinator.next()
        else:
            self.logger.warning("Zone %s not discovered" %zn)

    def prev(self, zn):
        if zn in self.zones:
            self.zones[zn].group.coordinator.previous()
        else:
            self.logger.warning("Zone %s not discovered" %zn)

    def volumeSet(self, zn, value):

        if zn in self.zones:
            value = int(value)
            if value < 0 or value > 100:
                self.logger.warning("Zone(%s): Illegal volume value: %d" % (zn, value))
                return

            # For volumeSet we set the volume for all zones in the group
            for m in self.zones[zn].group.members:
                m.volume = value
        else:
            self.logger.warning("Zone %s not discovered" %zn)

    def volumeUp(self, zn):
        if zn in self.zones:
            if self.zones[zn].volume < 100:
                self.zones[zn].volume += 1
        else:
            self.logger.warning("Zone %s not discovered" %zn)

    def volumeDown(self, zn):
        if zn in self.zones:
            if self.zones[zn].volume > 0:
                self.zones[zn].volume -= 1
        else:
            self.logger.warning("Zone %s not discovered" %zn)

    def setURI(self, zn, value):

        if zn in self.zones:
            self.logger.info("Setting URI: %s" % value)
            self.zones[zn].group.coordinator.play_uri(value, start=True)
        else:
            self.logger.warning("Zone %s not discovered" %zn)
