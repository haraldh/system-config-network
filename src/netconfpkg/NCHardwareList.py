from HardwareList import *
from os import *
from os.path import *
if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
import Conf

class HardwareList(HardwareList_base):
    def __init__(self, list = None, parent = None):
        HardwareList_base.__init__(self, list, parent)        

    def load(self):
        modules = Conf.ConfModules()
        modinfo = Conf.ConfModInfo()
        for i in modinfo.keys():
	    if modinfo[i]['type'] == "eth":
                pass

    def save(self):
        pass

if __name__ == '__main__':
    hl = HardwareList()
    hl.load()
    for i in xrange(len(hl)):
        print "Device: " + str(hl[i].DeviceId)
        print "DevName: " + str(hl[i].DeviceName)
        print "IP: " + str(hl[i].IP)
        print "OnBoot: " + str(hl[i].OnBoot)
        print "---------"

    hl.save()
