from ProfileList import *
from os import *
from os.path import *
if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
import Conf

class ProfileList(ProfileList_base):
    def __init__(self, list = None, parent = None):
        ProfileList_base.__init__(self, list, parent)        

    def load(self):
	i = self.addProfile()
        self.data[i].ProfileName = 'default'
	i = self.addProfile()
        self.data[i].ProfileName = 'work'

        modules = Conf.ConfModules()
        modinfo = Conf.ConfModInfo()
        for i in modinfo.keys():
	    if modinfo[i]['type'] == "eth":
                pass

    def save(self):
        pass

if __name__ == '__main__':
    pl = ProfileList()
    pl.load()
    for i in xrange(len(pl)):
        print "Device: " + str(pl[i].DeviceId)
        print "DevName: " + str(pl[i].DeviceName)
        print "IP: " + str(pl[i].IP)
        print "OnBoot: " + str(pl[i].OnBoot)
        print "---------"

    pl.save()
