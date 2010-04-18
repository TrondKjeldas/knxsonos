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
from brisa.core.network import parse_url
from brisa.upnp.control_point.control_point import ControlPoint

from time import sleep

import xml.etree.ElementTree as ET

from xmlevents import XmlEvent

avservice = ('u', 'urn:schemas-upnp-org:service:AVTransport:1')
rcservice = ('u', 'urn:schemas-upnp-org:service:RenderingControl:1')

def get_av_service(device):

    return device.services[avservice[1]]

def get_rc_service(device):

    return device.services[rcservice[1]]


class SonosCtrl():

    def __init__(self, zone_name):

        self.zone_name = zone_name

        self.current_server = None
        
        self.c = ControlPoint()
        self.c.subscribe('new_device_event', self.on_new_device)
        self.c.subscribe('removed_device_event', self.on_removed_device)

    def getCmdDict(self):
        """Return a dictionary that can be used to map commans to methods"""

        return { "play" : self.play,
                 "pause" : self.pause,
                 "next" : self.next,
                 "previous" : self.prev,
                 "volume+" : self.volumeUp,
                 "volume-" : self.volumeDown,
                 "volumeSet" : self.volumeSet }
    def start(self):

        self.c.start()
        self.c.start_search(30)

    def stop(self):

        self.c.stop()

    def on_new_device(self, dev):

        if not dev:
            return

        if self.current_server != None:
            print ("UPNP(%s): Already have wanted zone, "
                   "ignoring device: %s" %(self.zone_name,
                                           dev.friendly_name))
            return
        
        # Look for zone name...
        if dev.friendly_name.find(self.zone_name) != -1:
            self.current_server = dev
        elif dev.devices:
            for child_dev in dev.devices.values():
                if child_dev.friendly_name.find(self.zone_name) != -1:
                    self.current_server = child_dev

        # If we found our zone, subscribe to events...
        if self.current_server == None:
            print "UPNP(%s): Ignoring unwanted device: %s" %(self.zone_name,
                                                             dev.friendly_name)
        else:
            print "UPNP(%s): Found wanted zone: %s" %(self.zone_name,
                                                      dev.friendly_name)

            srv = get_av_service(self.current_server)
            srv.event_subscribe(self.c.event_host,
                                self._event_subscribe_callback,
                                None)

            srv.subscribe_for_variable("LastChange", self._event_callback)
            sleep(1)

    def on_removed_device(self, udn):
        
        print 'UPNP(%s): Device is gone: %s' %(self.zone_name, udn)

    def _event_subscribe_callback(self, cargo, subscription_id, timeout):

        print "UPNP(%s): Event subscribe done!" %self.zone_name
        print 'UPNP(%s): Subscription ID: %s' %(self.zone_name,
                                                str(subscription_id[5:]))
        print 'UPNP(%s): Timeout: %s' %(self.zone_name,
                                        str(timeout))

    def _event_callback(self, name, value):

        if name == "LastChange":
            print "UPNP(%s): Got event: %s" %(self.zone_name, name)
            ev = XmlEvent(value)
            ev.dump()
        else:
            print "UPNP(%s): Ignoring unknown event: %s" %(self.zone_name,
                                                           name)


    def print_status(self, status):

            print "UPNP(%s): Status: %s" %(self.zone_name, str(status))
        
    def pause(self):
        if self.current_server != None:
            service = get_av_service(self.current_server)
            status_response = service.Pause(InstanceID=0)
            self.print_status(status_response)

    def play(self):
        if self.current_server != None:
            service = get_av_service(self.current_server)
            status_response = service.Play(InstanceID=0, Speed=1)
            self.print_status(status_response)

    def next(self):
        if self.current_server != None:
            service = get_av_service(self.current_server)
            status_response = service.Next(InstanceID=0)
            self.print_status(status_response)

    def prev(self):
        if self.current_server != None:
            service = get_av_service(self.current_server)
            status_response = service.Previous(InstanceID=0, Speed=1)
            self.print_status(status_response)

    def volumeSet(self, value):
        if self.current_server != None:
            value = int(value)
            if value < 0 or value > 100:
                print "UPNP(%s): Illegal volume value: %d" %(self.zone_name,
                                                             value)
                return
            
            service = get_rc_service(self.current_server)
            status_response = service.SetVolume(InstanceID=0,
                                                Channel="Master",
                                                DesiredVolume=value)
            self.print_status(status_response)

    def volumeUp(self):
        if self.current_server != None:
            service = get_rc_service(self.current_server)
            status_response = service.SetRelativeVolume(InstanceID=0,
                                                        Channel="Master",
                                                        Adjustment=3)
            self.print_status(status_response)

    def volumeDown(self):
        if self.current_server != None:
            service = get_rc_service(self.current_server)
            status_response = service.SetRelativeVolume(InstanceID=0,
                                                        Channel="Master",
                                                        Adjustment=-3)
            self.print_status(status_response)
