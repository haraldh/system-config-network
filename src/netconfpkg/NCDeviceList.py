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
        self.commit()

    def save(self):
        try:
            dir = listdir(SYSCONFDEVICEDIR)
        except OSError, msg:
            raise IOError, 'Cannot save in ' \
                  + SYSCONFDEVICEDIR + ': ' + str(msg)

        try: 
            for entry in dir:
                if (len(entry) <= 6) or \
                   entry[:6] != 'ifcfg-' or \
                   (not isfile(SYSCONFDEVICEDIR + entry)):
                    #print "skipping " + entry
                    continue
                
                devid = entry[6:]

                try:
                    found = false
                    #print "searching for " + devid
                    for dev in self:
                        if dev.DeviceId == devid:
                            found = true
                            break
                    if not found:
                        unlink(SYSCONFDEVICEDIR + entry)
                except OSError, msg:
                    raise IOError, 'Error removing old device. ' + str(msg)
        finally:            
            for dev in self:
                dev.save()

        self.commit()

DVList = None

def getDeviceList():
    global DVList
    if not DVList:
        DVList = DeviceList()
        DVList.load()
    return DVList

                
if __name__ == '__main__':
    dl = DeviceList()
    dl.load()
    for dev in dl:
        print "ID: " + str(dev.DeviceId)
        print "Device: " + str(dev.Device)
        print "Name: " + str(dev.Name)
        print "IP: " + str(dev.IP)
        print "OnBoot: " + str(dev.OnBoot)
        print "Type: " + str(dev.Type)
        print "---------"
    dl.save()
