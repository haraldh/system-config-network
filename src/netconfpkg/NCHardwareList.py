import sys
import os
import string

from HardwareList import *
from NCisdnhardware import *

import NC_functions

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
        wvdial = ConfSMB('/etc/wvdial.conf')

        for mod in modules.keys():
            type = NC_functions.getDeviceType(mod)
            if type == 'Unknown':
                continue

            i = self.addHardware()
            hw = self.data[i]
            hw.Name = mod
            hw.Description = mod
            hw.Type = type
            hw.createCard()
            for info in modinfo.keys():
                if info == modules[mod]['alias'] and modinfo[info]['type'] == 'eth':
                    hw.Card.ModuleName = info
                    hw.Description = modinfo[info]['description']

                    # for h in hwconf.keys():
                    #     if hwconf[h]['driver'] == info:
                    #         pass

        
        isdncard = ConfISDN()
        if isdncard.load() > 0:
            i = self.addHardware()
            hw = self.data[i]
            hw.Name = "ISDN Card 0"
            hw.Description = isdncard.Description
            hw.Type = "ISDN"
            hw.createCard()
            hw.Card.ModuleName = isdncard.ModuleName
            hw.Card.Type = isdncard.Type
            hw.Card.IoPort = isdncard.IoPort
            hw.Card.IoPort1 = isdncard.IoPort1
            hw.Card.IoPort2 = isdncard.IoPort2
            hw.Card.Mem = isdncard.Mem
            hw.Card.IRQ = isdncard.IRQ
            hw.Card.ChannelProtocol = isdncard.ChannelProtocol
            hw.Card.Firmware = isdncard.Firmware
            
        wvdial = ConfSMB('/etc/wvdial.conf')
        for dev in wvdial.keys():
            if dev[:5] != 'Modem':
                continue

            i = self.addHardware()
            hw = self.data[i]
            hw.Name = dev
            hw.Description = 'Generic Modem'
            hw.Type = 'Modem'
            hw.createModem()
            hw.Modem.DeviceName = wvdial[dev]['Modem']
            hw.Modem.BaudRate = wvdial[dev]['Baud']
            hw.Modem.ModemVolume = wvdial[dev]['SetVolume']
            hw.Modem.DialCommand = wvdial[dev]['Dial Command']
        self.commit()

    def save(self):
        modules = ConfModules()
        wvdial  = ConfSMB('/etc/wvdial.conf')
        isdn    = ConfISDN()
        
        for hw in self.data:
            if hw.Type == 'Ethernet':
                modules[hw.Name]['alias'] = hw.Card.ModuleName
            if hw.Type == 'Modem':
                wvdial[hw.Name]['Modem'] = hw.Modem.DeviceName
                wvdial[hw.Name]['Baud'] = str(hw.Modem.BaudRate)
                wvdial[hw.Name]['SetVolume'] = str(hw.Modem.ModemVolume)
                wvdial[hw.Name]['Dial Command'] = str(hw.Modem.DialCommand)
            if hw.Type == "ISDN":
                isdn.Description = hw.Description
                isdn.Type = hw.Card.Type
                isdn.ModulName = hw.Card.ModuleName
                isdn.IRQ = hw.Card.IRQ
                isdn.IoPort = hw.Card.IoPort
                isdn.IoPort1 = hw.Card.IoPort1
                isdn.IoPort2 = hw.Card.IoPort2
                isdn.Mem = hw.Card.Mem
                isdn.ChannelProtocol = hw.Card.ChannelProtocol
                isdn.Firmware = hw.Card.Firmware
                isdn.Id = "HiSax"

        modules.write()
        wvdial.write()
        isdn.save()

HWList = None

def getHardwareList():
    global HWList
    if HWList == None:
        HWList = HardwareList()
        HWList.load()
    return HWList


if __name__ == '__main__':
    hl = HardwareList()
    hl.load()
    for i in xrange(len(hl)):
        print "Name: ", hl[i].Name
        print "Description: ", hl[i].Description
        print "Type: ", hl[i].Type
        if hl[i].Type == "Ethernet" or hl[i].Type == "ISDN":
            print "ModuleName: ", hl[i].Card.ModuleName
            print "IoPort: ", hl[i].Card.IoPort
            print "IoPort1: ", hl[i].Card.IoPort1
            print "IoPort2: ", hl[i].Card.IoPort2
            print "Mem: ", hl[i].Card.Mem
            print "IRQ: ", hl[i].Card.IRQ
            print "DMA0: ", hl[i].Card.DMA0
            print "DMA1: ", hl[i].Card.DMA1
            print "ChannelProtocol: ", hl[i].Card.ChannelProtocol
            
        if hl[i].Type == "Modem":
            print "DeviceName: ", hl[i].Modem.DeviceName
            print "BaudRate: ", hl[i].Modem.BaudRate
            print "FlowControl: ", hl[i].Modem.FlowControl
            print "ModemVolume: ", hl[i].Modem.ModemVolume
            print "DialCommand: ", hl[i].Modem.DialCommand

        print "-----------------------------------------"

    hl.save()
