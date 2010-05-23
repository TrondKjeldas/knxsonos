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
from StringIO import StringIO

class XmlEvent():

    def makefile(self, s):

        f = StringIO(s)
        f.seek(0)
        return f


class LastChangeEvent(XmlEvent):

    def __init__(self, event):

        f = self.makefile(event)
        self.root = ET.parse(f).getroot()
        
        instances = self.root.findall('{urn:schemas-upnp-org:metadata-1-0/AVT/}'
                                      'InstanceID')
        
        if len(instances) != 1:
            print "XML:  Incorrect number of instances!"
            
        inst = instances[0]
    
        self.emap = {}
        for e in inst:
            tn = e.tag[e.tag.find('}')+1:]
            self.emap[tn] = e.attrib["val"]
    
        self.emap["DecodedCurrentTrackMetaData"] = self.parse_TrackMetaData(
            self.emap["CurrentTrackMetaData"])

        self.emap["DecodedNextTrackMetaData"] = self.parse_TrackMetaData(
            self.emap["NextTrackMetaData"])


    def makefile(self, s):

        f = StringIO(s)
        f.seek(0)
        return f

    def parse_TrackMetaData(self, s):
        root = ET.parse(self.makefile(s)).getroot()
        
        i = root.find("{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}item")
        
        c  = i.find("{http://purl.org/dc/elements/1.1/}creator")
        aa = i.find("{urn:schemas-rinconnetworks-com:metadata-1-0/}albumArtist")
        t  = i.find("{http://purl.org/dc/elements/1.1/}title")
        
        return (c.text, aa.text, t.text)

    def dump(self):

        print "XML:  State:"
        print "XML:     %s" %self.emap["TransportState"]
        
        c, aa, t = self.emap["DecodedCurrentTrackMetaData"]
        print "XML:  Current:"
        print "XML:     Creator: " + c
        print "XML:     Album Artist: " + aa
        print "XML:     Title: " + t
        
        c, aa, t = self.emap["DecodedNextTrackMetaData"]        
        print "XML:  Next:"
        print "XML:     Creator: " + c
        print "XML:     Album Artist: " + aa
        print "XML:     Title: " + t
        

class ZoneGroupEvent(XmlEvent):

    def __init__(self, event):

        f = self.makefile(event)
        self.root = ET.parse(f).getroot()
        
        self.groups = []

        _gs   = self.root.findall("ZoneGroup")
        for g in _gs:
            coord = g.attrib["Coordinator"]
            _members = g.findall("ZoneGroupMember")
            members = [ m.attrib["UUID"] for m in _members ]
            self.groups.append( (coord, members) )


    def dump(self):
            
        for coordinator,members in self.groups:
            print "Coordinator: %s" %coordinator
            print "Members:     %s" %members
            print
    


# <ZoneGroups>
#    <ZoneGroup Coordinator="RINCON_000E58334C5A01400" ID="RINCON_000E58334C5A01400:25">
#        <ZoneGroupMember UUID="RINCON_000E58334C5A01400" Location="http://192.168.1.66:1400/xml/zone_player.xml" ZoneName="Bathroom" Icon="x-rincon-roomicon:bathroom" SoftwareVersion="13.7-29120" MinCompatibleVersion="12.0-00000" BootSeq="5"/>
#        <ZoneGroupMember UUID="RINCON_000E58334AF601400" Location="http://192.168.1.175:1400/xml/zone_player.xml" ZoneName="Kitchen" Icon="x-rincon-roomicon:kitchen" SoftwareVersion="13.7-29120" MinCompatibleVersion="12.0-00000" BootSeq="5"/>
#    </ZoneGroup>
#    <ZoneGroup Coordinator="RINCON_000E5812D0DA01400" ID="RINCON_000E58334AF601400:10">
#       <ZoneGroupMember UUID="RINCON_000E5812D0DA01400" Location="http://192.168.1.39:1400/xml/zone_player.xml" ZoneName="Living Room" Icon="x-rincon-roomicon:living" SoftwareVersion="13.7-29120" MinCompatibleVersion="12.0-00000" BootSeq="51"/>
#     </ZoneGroup>
# </ZoneGroups> 
