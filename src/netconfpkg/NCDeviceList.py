from DeviceList import *
from os import *
from os.path import *
if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
import Conf
from NC_functions import *

class ConfDevices(UserList.UserList):
    def __init__(self):
        UserList.UserList.__init__(self)

        #for confdir in [ SYSCONFDEVICEDIR, OLDSYSCONFDEVICEDIR ]:
        confdir = SYSCONFDEVICEDIR    
        try:
            dir = listdir(confdir)
        except OSError, msg:
            pass
        else:
            for entry in dir:
                if (len(entry) > 6) and \
                   entry[:6] == 'ifcfg-' and \
                   isfile(confdir + entry):
                    self.append(entry[6:])
        return

class DeviceList(DeviceList_base):
    def __init__(self, list = None, parent = None):
        DeviceList_base.__init__(self, list, parent)        

    def load(self):
        devices = ConfDevices()
        for dev in devices:
            i = self.addDevice()
            self.data[i].load(dev)

    def save(self):
        try:
            dir = listdir(SYSCONFDEVICEDIR)
        except OSError, msg:
            raise IOError, 'Cannot save in ' \
                  + SYSCONFDEVICEDIR + ': ' + str(msg)

        try: 
            for entry in dir:
                try:
                    if(isfile(SYSCONFDEVICEDIR + entry)):
                        unlink(SYSCONFDEVICEDIR + entry)
                except OSError, msg:
                    raise IOError, 'Error removing old device. ' + str(msg)
        finally:            
            for i in xrange(len(self)):
                self.data[i].save()

if __name__ == '__main__':
    dl = DeviceList()
    dl.load()
    for i in xrange(len(dl)):
        print "ID: " + str(dl[i].DeviceId)
        print "Device: " + str(dl[i].Device)
        print "Name: " + str(dl[i].Name)
        print "IP: " + str(dl[i].IP)
        print "OnBoot: " + str(dl[i].OnBoot)
        print "---------"

    dl.save()
