import os
import string
from HardwareList import *
if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
from Conf import *
from ConfSMB import *

class ConfHWConf(Conf):
    def __init__(self):
        Conf.__init__(self, '/etc/sysconfig/hwconf')

    def read(self):
        Conf.read(self)
        self.initvars()

    def initvars(self):
        self.vars = {}

        if not os.access("/etc/sysconfig/hwconf", os.R_OK):
            return

        fp = open('/etc/sysconfig/hwconf', 'r')
        hwlist = fp.read()
        hwlist = string.split(hwlist, "-\n")
        pos = 0
        for hw in hwlist:
            if not len(hw):
                continue
            items = string.split(hw, '\n')
            hwdict = {}
            for item in items:
                if not len(item):
                    continue
                vals = string.split(item, ":")
                if len(vals) <= 1:
                    # skip over bad/malformed lines
                    continue
                # Some of the first words are used as dict keys server side
                # so this just helps make that easier
                strippedstring = string.strip(vals[1])
                vals[1] = strippedstring
                hwdict[vals[0]] = string.join(vals[1:])
            self.vars[pos] = hwdict
            pos = pos + 1

    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return None

    def keys(self):
        return self.vars.keys()

class HardwareList(HardwareList_base):
    def __init__(self, list = None, parent = None):
        HardwareList_base.__init__(self, list, parent)        

    def load(self):
        modules = ConfModules()
        modinfo = ConfModInfo()
        hwconf = ConfHWConf()
        for mod in modules.keys():
            type = getDeviceType(mod)
            if type == 'Unknown':
                continue

            i = self.addHardware()
            hw = self.data[i]
            hw.createCard()
            hw.Name = mod
            hw.Description = mod
            hw.Type = type
            hw.Card.DeviceName = mod
            for info in modinfo.keys():
                if info == modules[mod]['alias'] and modinfo[info]['type'] == 'eth':
                    hw.Description = modinfo[info]['description']
                    for h in hwconf.keys():
                        if hwconf[h]['driver'] == info:
                            pass

        #wvdial = ConfSMB('/etc/wvdial.conf')
        wvdial = ConfSMB('/etc/samba/smb.conf')
        for dev in wvdial.keys():
            print dev,wvdial[dev]

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
