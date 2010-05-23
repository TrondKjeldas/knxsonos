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

from xmlevents import LastChangeEvent, ZoneGroupEvent


friendly_name = {}
zone_from_udn = {}

avservice = ('u', 'urn:schemas-upnp-org:service:AVTransport:1')
rcservice = ('u', 'urn:schemas-upnp-org:service:RenderingControl:1')
ztservice = ('u', 'urn:schemas-upnp-org:service:ZoneGroupTopology:1')

def get_av_service(device):

    return device.services[avservice[1]]

def get_rc_service(device):

    return device.services[rcservice[1]]

def get_zt_service(device):

    return device.services[ztservice[1]]

class SonosZone():

    def __init__(self, name, device, parent):

        self.name = name
        self.udn = device.udn
        self.dev = device
        self.parent = parent
        self.current_coordinator = self

    def setCoordinator(self, coord):

        #print "New coordinator: %s" %coord
        if coord in zone_from_udn.keys():
            self.current_coordinator = zone_from_udn[coord]
        else:
            print "Failed to set new coordinator: %s" %coord
            print "Known devices: %s" %zone_from_udn.keys()
            
    
class SonosCtrl():

    def __init__(self, zone_names):

        self.zones = {}
        
        for name in zone_names:

            self.zones[name] = None

        
        self.c = ControlPoint()
        self.c.subscribe('new_device_event', self.on_new_device)
        self.c.subscribe('removed_device_event', self.on_removed_device)
        #self.c.subscribe('device_event', self._event_callback)

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

        self.c.start()
        self.c.start_search(30)

    def stop(self):

        self.c.stop()

    def on_new_device(self, dev):

        if not dev:
            return

        found = None
        parent = None
        duplicate = False
        for zn in self.zones.keys():
            # Look for zone name...
            if dev.friendly_name.find(zn) != -1:
                if self.zones[zn] == None:
                    self.zones[zn] = SonosZone(zn, dev, None)
                    found = dev
                    break
                else:
                    duplicate = True
            elif dev.devices:
                for child_dev in dev.devices.values():
                    if child_dev.friendly_name.find(zn) != -1:
                        if self.zones[zn] == None:
                            self.zones[zn] = SonosZone(zn, child_dev, dev)
                            found = child_dev
                            parent = dev
                            break
                        else:
                            duplicate = True
                if found != None:
                    break
                        

        if found == None:
            print "UPNP: Ignoring unwanted device: %s" %dev.friendly_name
            return
        elif duplicate:
            print "UPNP: Already have zone: %s" %dev.friendly_name
            return
        elif parent == None:
            print "UPNP: Found a zone media renderer, but no parrent?"
            return
        
        # If we found our zone, subscribe to events...
        print "UPNP: Found wanted zone: %s(%s)" %(found.friendly_name,
                                                  parent.udn)

        # Add a mappings between the UDN and the zone name,
        # as well as UDN and SonosZone instance...
        friendly_name[parent.udn[5:]] = found.friendly_name.replace(" - Sonos ZonePlayer Media Renderer", "")
        zone_from_udn[parent.udn[5:]] = self.zones[zn]
        

        # When all zones found, do subscriptions...
        if None not in self.zones.values():
            self._doSubscriptions()
        
    def on_removed_device(self, udn):
        
        print 'UPNP: Device is gone: %s' %udn

    def _doSubscriptions(self):

        for z in self.zones.values():
            
            srv = get_av_service(z.dev)
            srv.event_subscribe(self.c.event_host,
                                self._event_subscribe_callback,
                                None)
        
            srv.subscribe_for_variable("LastChange", self._av_event_callback)
            
            srv = get_rc_service(z.dev)
            srv.event_subscribe(self.c.event_host,
                                self._event_subscribe_callback,
                                None)
            
            srv.subscribe_for_variable("LastChange", self._rc_event_callback)
            
            srv = get_zt_service(z.parent)
            srv.event_subscribe(self.c.event_host,
                                self._event_subscribe_callback,
                                None)
            
            srv.subscribe_for_variable("ZoneGroupState", self._event_topology)
            
            sleep(1)
        
    def _event_subscribe_callback(self, cargo, subscription_id, timeout):

        print "UPNP: Event subscribe done!"
        #print 'UPNP: Subscription ID: %s' %str(subscription_id[5:])
        #print 'UPNP: Timeout: %s' %str(timeout)

    def _av_event_callback(self, name, value):

        if name == "LastChange":
            print "UPNP: Got event: %s" %name
            #print "UPNP: Got event: %s" %value
            ev = LastChangeEvent(value)
            ev.dump()
        else:
            print "UPNP: Ignoring unknown event: %s" %name
            #print "UPNP: Ignoring unknown event: %s(%s)" %(name,value)

    def _rc_event_callback(self, name, value):

        if name == "LastChange":
            print "UPNP: Got event: %s" %name
            #print "UPNP: Got event: %s" %value
            #ev = LastChangeEvent(value)
            #ev.dump()
        else:
            print "UPNP: Ignoring unknown event: %s" %name
            #print "UPNP: Ignoring unknown event: %s(%s)" %(name,value)

    def _event_topology(self, name, value):

        if name == "ZoneGroupState":
            ev = ZoneGroupEvent(value)
            for coordinator,members in ev.groups:
                
                # Update current_coordinator in all the member zones...
                for m in members:
                    try:
                        zone_from_udn[m].setCoordinator(coordinator)
                    except:
                        print "failed!"
                        print coordinator
                        print zone_from_udn

                # Print info...
                print "Coordinator: %s" %friendly_name[coordinator]
                members = [ friendly_name[m] for m in members ]
                print "Members:     %s" %members
        else:
            print "UPNP: Ignoring unknown event: %s(%s)" %(name,value)

    def print_status(self, zone_name, status):

            print "UPNP(%s): Status: %s" %(zone_name, str(status))

    def get_server(self, zone_name):

        if zone_name in self.zones.keys():
            return self.zones[zone_name].dev
        
        return None

    def get_coordinator(self, zone_name):

        # As get_server, but redirects to group coordinator
        # if the zone is in a group...
        if zone_name in self.zones.keys():
            return self.zones[zone_name].current_coordinator.dev

        return None
    
    def pause(self, zn):
        if self.get_coordinator(zn) != None:
            service = get_av_service(self.get_coordinator(zn))
            status_response = service.Pause(InstanceID=0)
            self.print_status(zn, status_response)

    def play(self, zn):
        if self.get_coordinator(zn) != None:
            service = get_av_service(self.get_coordinator(zn))
            status_response = service.Play(InstanceID=0, Speed=1)
            self.print_status(zn, status_response)

    def next(self, zn):
        if self.get_coordinator(zn) != None:
            service = get_av_service(self.get_coordinator(zn))
            status_response = service.Next(InstanceID=0)
            self.print_status(zn, status_response)

    def prev(self, zn):
        if self.get_coordinator(zn) != None:
            service = get_av_service(self.get_coordinator(zn))
            status_response = service.Previous(InstanceID=0, Speed=1)
            self.print_status(zn, status_response)

    def volumeSet(self, zn, value):
        if self.get_server(zn) != None:
            value = int(value)
            if value < 0 or value > 100:
                print "UPNP(%s): Illegal volume value: %d" %(self.zone_name,
                                                             value)
                return
            
            service = get_rc_service(self.get_server(zn))
            status_response = service.SetVolume(InstanceID=0,
                                                Channel="Master",
                                                DesiredVolume=value)
            self.print_status(zn, status_response)

    def volumeUp(self, zn):
        if self.get_server(zn) != None:
            service = get_rc_service(self.get_server(zn))
            status_response = service.SetRelativeVolume(InstanceID=0,
                                                        Channel="Master",
                                                        Adjustment=3)
            self.print_status(zn, status_response)

    def volumeDown(self, zn):
        if self.get_server(zn) != None:
            service = get_rc_service(self.get_server(zn))
            status_response = service.SetRelativeVolume(InstanceID=0,
                                                        Channel="Master",
                                                        Adjustment=-3)
            self.print_status(zn, status_response)

    def setURI(self, zn, value):
        if self.get_coordinator(zn) != None:
            
            service = get_av_service(self.get_coordinator(zn))
            print "Setting URI: %s" %value
            status_response = service.SetAVTransportURI(InstanceID=0,
                                                        CurrentURI=value,
                                                        CurrentURIMetaData="")
            self.print_status(zn, status_response)
