
from brisa.core.network import parse_url
from brisa.upnp.control_point.control_point import ControlPoint

avservice = ('u', 'urn:schemas-upnp-org:service:AVTransport:1')
rcservice = ('u', 'urn:schemas-upnp-org:service:RenderingControl:1')

def get_av_service(device):

    return device.services[avservice[1]]

def get_rc_service(device):

    return device.services[rcservice[1]]


class SonosCtrl():

    def __init__(self):

        self.c = ControlPoint()
        self.c.subscribe('new_device_event', self.on_new_device)
        self.c.subscribe('removed_device_event', self.on_removed_device)
        self.c.subscribe('device_event', self.on_removed_device)

    def start(self):

        self.c.start()
        self.c.start_search(30)

    def stop(self):

        self.c.stop()

    def on_new_device(self, dev):

        if not dev:
            return
        
        print 'Got new device:', dev.udn
        
        self.list_devices()

    def on_removed_device(udn):
        print 'Device is gone:', udn

    def list_devices(self):

        for d in self.c.get_devices().values():
            print 'UDN:', d.udn
            print 'Name:', d.friendly_name
            print 'Device type:', d.device_type
            print 'Services:', d.services.keys() # Only print services name
            ed = [dev.friendly_name for dev in d.devices.values()]
            print 'Embedded devices:', ed # Only print embedded devices names
            if len(ed) > 0:
                self.c.current_server = d.devices.values()[0]
                print "CURRENT: %s" % self.c.current_server.friendly_name

                srv = get_av_service(self.c.current_server)
                srv.subscribe_for_variable("CurrentTrack", self._curtrack)
            print



    def pause(self):
        service = get_av_service(self.c.current_server)
        status_response = service.Pause(InstanceID=0)
        print "STATUS: %s" %str(status_response)

    def play(self):
        service = get_av_service(self.c.current_server)
        status_response = service.Play(InstanceID=0, Speed=1)
        print "STATUS: %s" %str(status_response)

    def next(self):
        service = get_av_service(self.c.current_server)
        status_response = service.Next(InstanceID=0)
        print "STATUS: %s" %str(status_response)

    def prev(self):
        service = get_av_service(self.c.current_server)
        status_response = service.Previous(InstanceID=0, Speed=1)
        print "STATUS: %s" %str(status_response)

    def volup(self):
        service = get_rc_service(self.c.current_server)
        print "SERVICE: %s" %str(service.__dict__.keys())
        status_response = service.SetRelativeVolume(InstanceID=0,
                                                Channel="Master",
                                                Adjustment=1)
        print "STATUS: %s" %str(status_response)

    def voldown(self):
        service = get_rc_service(self.c.current_server)
        status_response = service.SetRelativeVolume(InstanceID=0,
                                                    Channel="Master",
                                                    Adjustment=-1)
        print "STATUS: %s" %str(status_response)

    def _curtrack(self):
        
        print "Track change"
        
    def _gettrack(c):
        srv = get_av_service(self.c.current_server)
        print "TRACK: %s" %str(srv.get_state_variable("CurrentTrack").__dict__)
    
    def commands(self):

        return {'pause': self.pause,
                'play': self.play,
                'next': self.next,
                'prev': self.prev,
                '+': self.volup,
                '-': self.voldown,
                'gett' : self._gettrack}


    def testing(self):

        GetMediaInfo(InstanceID=0)
        
