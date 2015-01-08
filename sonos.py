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
import soco


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

        self.zones = {}
        for name in zone_names:
            self.zones[name] = None


    def getCmdDict(self):
        """Return a dictionary that can be used to map commans to methods"""

        return { "play" : self.play,
                 "pause" : self.pause,
                 "next" : self.next,
                 "previous" : self.prev,
                 "volume+" : self.volumeUp,
                 "volume-" : self.volumeDown,
                 "volumeSet" : self.volumeSet,
                 "setURI" : self.setURI }

    def start(self):

        zs = list(soco.discover())
        for z in zs:
            print z
            self.zones[z.player_name] = z
        

        print "Found zones:"
        for k,v in self.zones.items():
            print "     %s" %k

    def stop(self):
        pass

    #
    # Sonos commands
    #

    def pause(self, zn):
        self.zones[zn].group.coordinator.pause()

    def play(self, zn):
        self.zones[zn].group.coordinator.play()

    def next(self, zn):
        self.zones[zn].group.coordinator.next()

    def prev(self, zn):
        self.zones[zn].group.coordinator.previous()

    def volumeSet(self, zn, value):

        value = int(value)
        if value < 0 or value > 100:
            print "Zone(%s): Illegal volume value: %d" %(zn, value)
            return
            
        self.zones[zn].group.coordinator.volume = value

    def volumeUp(self, zn): 
        if self.zones[zn].group.coordinator.volume < 100:
            self.zones[zn].group.coordinator.volume += 1

    def volumeDown(self, zn):
        if self.zones[zn].group.coordinator.volume > 0:
            self.zones[zn].group.coordinator.volume -= 1


    def setURI(self, zn, value):

        print "Setting URI: %s" %value
        self.zones[zn].group.coordinator.play_uri(value, start=True)

