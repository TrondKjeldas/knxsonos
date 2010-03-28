import xml.etree.ElementTree as ET
from StringIO import StringIO

class XmlEvent():

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
        
