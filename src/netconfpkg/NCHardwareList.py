## Copyright (C) 2001, 2002 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001, 2002 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sys
import os
import string
from rhpl import ethtool
import NCisdnhardware

from netconfpkg import HardwareList_base
from netconfpkg.NCHardware import Hardware
from NC_functions import *

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

from rhpl.Conf import *
from rhpl.ConfSMB import *

ModInfo = None

def getModInfo():
    global ModInfo
    if ModInfo == None:
        try:
            ModInfo = ConfModInfo(filename = '/boot/module-info')
        except (VersionMismatch, FileMissing):
            # ok, take fallback
            ModInfo = ConfModInfo(filename = NETCONFDIR + '/module-info')
    return ModInfo

class MyConfModules(ConfModules):
    def __init__(self, filename = '/etc/modules.conf'):
        ConfModules.__init__(self, filename)
        
    def __delitem__(self, varname):
        # delete *every* instance...
        place=self.tell()
        for key in self.vars[varname].keys():
            self.rewind()

            # workaround for broken regexp implementation
            restr = '^[\\t ]*' + key + '[\\t ]+' + varname
            while self.findnextline(restr):
                #print "1) Deleting %s" % self.line
                self.deleteline()

            restr = '^[\\t ]*' + key + '[\\t ]+\\-k[\\t ]+' + varname
            while self.findnextline(restr):
                #print "2) Deleting %s" % self.line
                self.deleteline()

        del self.vars[varname]
        #print "del self.vars[%s]" % varname
        self.seek(place)
        
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
        self.keydict = { 'IoPort' : 'io',
                         'IRQ' : 'irq',
                         'Mem' : 'mem',
                         'DMA0' : 'dma',
        }


    def addHardware(self, type = None):
        from netconfpkg.NCHardwareFactory import getHardwareFactory
        i = HardwareList_base.addHardware(self)
        hwf = getHardwareFactory()
        hwc = hwf.getHardwareClass(type)
        if hwc:
            newhw = hwc()
            self[i] = newhw
        return i

    def updateFromSystem(self):
        modules = ConfModules()
        modinfo = getModInfo()
        #
        # Read in actual system state
        #
        for device in ethtool.get_devices():
            if device[:3] != "eth":
                continue

            # No Alias devices
            if string.find(device, ':') != -1:
                continue

            try:
                mod = ethtool.get_module(device)
            except IOError, err:
                mod = None

            if mod != None and mod != "":
                for hw in self:
                    if hw.Name == device:
                        if hw.Card and hw.Card.ModuleName != mod:
                            generic_error_dialog (\
                                _("%s has an alias to module %s in modules.conf,\ninstead of currently loaded module %s!") % (hw.Name, hw.Card.ModuleName, mod))
                        break
                else:
                    i = self.addHardware(getDeviceType(device))
                    hw = self[i]
                    hw.Name = device
                    hw.Description = mod
                    hw.Type = getDeviceType(device)
                        
                    hw.createCard()
                    hw.Card.ModuleName = mod
                    for info in modinfo.keys():
                        if info == mod:
                            if modinfo[info].has_key('description'):
                                hw.Description = modinfo[info]['description']

                    for selfkey in self.keydict.keys():
                        confkey = self.keydict[selfkey]
                        if modules[hw.Card.ModuleName] and modules[hw.Card.ModuleName]['options'].has_key(confkey):
                            hw.Card.__dict__[selfkey] = modules[hw.Card.ModuleName]['options'][confkey]

    def load(self):
        modules = ConfModules()
        modinfo = getModInfo()
        hwconf = ConfHWConf()          

        #
        # Read /etc/modules.conf
        #
        for mod in modules.keys():
            if modules[mod].has_key('alias'):
                module = modules[mod]['alias']
            else: module = None
            
            type = getDeviceType(mod)
            if type == _('Unknown'):
                continue

            i = self.addHardware(type)
            hw = self[i]
            hw.Name = mod
            hw.Description = module
            hw.Type = type
            hw.createCard()
            hw.Card.ModuleName = module
            if module:
                for info in modinfo.keys():
                    if info == module:
                        if modinfo[info].has_key('description'):
                            hw.Description = modinfo[info]['description']

            for selfkey in self.keydict.keys():
                confkey = self.keydict[selfkey]
                if modules[hw.Card.ModuleName] and modules[hw.Card.ModuleName]['options'].has_key(confkey):
                    hw.Card.__dict__[selfkey] = modules[hw.Card.ModuleName]['options'][confkey]
                    
        self.updateFromSystem()

        isdncard = NCisdnhardware.ConfISDN()
        if isdncard.load() > 0:
            i = self.addHardware(ISDN)
            hw = self[i]
            hw.Name = "ISDN Card 0"
            hw.Description = isdncard.Description
            hw.Type = ISDN
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
            hw.Card.DriverId = isdncard.DriverId
            hw.Card.VendorId = isdncard.VendorId
            hw.Card.DeviceId = isdncard.DeviceId
            
        try:
            wvdial = ConfSMB('/etc/wvdial.conf')
        except Conf.FileMissing:
            pass
        else:
            for dev in wvdial.keys():
                if dev[:5] != 'Modem':
                    continue

                i = self.addHardware(MODEM)
                hw = self[i]
                hw.Name = dev
                hw.Description = 'Generic Modem'
                hw.Type = MODEM
                hw.createModem()
                if not wvdial[dev].has_key('Modem'):
                    wvdial[dev]['Modem'] = '/dev/modem'
                hw.Modem.DeviceName = wvdial[dev]['Modem']

                if not wvdial[dev].has_key('Baud'):
                    wvdial[dev]['Baud'] = '38400'
                hw.Modem.BaudRate = int(wvdial[dev]['Baud'])

                if not wvdial[dev].has_key('SetVolume'):
                    wvdial[dev]['SetVolume'] = '0'
                hw.Modem.ModemVolume = int(wvdial[dev]['SetVolume'])

                if not wvdial[dev].has_key('Dial Command'):
                    wvdial[dev]['Dial Command'] = 'ATDT'
                hw.Modem.DialCommand = wvdial[dev]['Dial Command']

                if not wvdial[dev].has_key('Init1'):
                    wvdial[dev]['Init1'] = 'ATZ'
                hw.Modem.InitString =  wvdial[dev]['Init1']

                if not wvdial[dev].has_key('FlowControl'):
                    wvdial[dev]['FlowControl'] = CRTSCTS
                hw.Modem.FlowControl =  wvdial[dev]['FlowControl']

        self.commit(changed=false)

    def save(self):
        modules = MyConfModules()
        if not os.access('/etc/wvdial.conf', os.R_OK):
            wvdial  = None
        else:
            wvdial = ConfSMB('/etc/wvdial.conf')

        isdn    = NCisdnhardware.ConfISDN()
        

        for hw in self:
            if hw.Type == ETHERNET:
                dic = modules[hw.Name]
                dic['alias'] = hw.Card.ModuleName
                modules[hw.Name] = dic

                # No, no, no... only delete known options!!!
                #WRONG: modules[hw.Card.ModuleName] = {}
                #WRONG: modules[hw.Card.ModuleName]['options'] = {}
                #
                # Better do it this way!
                if modules[hw.Card.ModuleName].has_key('options'):
                    for (key, confkey) in self.keydict.items():
                        if modules[hw.Card.ModuleName]['options'].has_key(confkey):
                            del modules[hw.Card.ModuleName]['options'][confkey]

                for (selfkey, confkey) in self.keydict.items():
                    if hw.Card.__dict__[selfkey]:
                        if selfkey == 'IRQ' \
                           and (hw.Card.IRQ == _('Unknown') \
                                or (hw.Card.IRQ == 'Unknown')):
                            continue
                        dic = modules[hw.Card.ModuleName]
                        if not dic.has_key('options'):
                            dic['options'] = {}
                        dic['options'][confkey] = str(hw.Card.__dict__[selfkey])
                        modules[hw.Card.ModuleName] = dic


            if hw.Type == TOKENRING:
                dic = modules[hw.Name]
                dic['alias'] = hw.Card.ModuleName
                modules[hw.Name] = dic

                # No, no, no... only delete known options!!!
                #WRONG: modules[hw.Card.ModuleName] = {}
                #WRONG: modules[hw.Card.ModuleName]['options'] = {}
                #
                # Better do it this way!
                if modules[hw.Card.ModuleName].has_key('options'):
                    for (key, confkey) in self.keydict.items():
                        if modules[hw.Card.ModuleName]['options'].has_key(confkey):
                            del modules[hw.Card.ModuleName]['options'][confkey]

                for (selfkey, confkey) in self.keydict.items():
                    if hw.Card.__dict__[selfkey]:
                        if selfkey == 'IRQ' \
                           and (hw.Card.IRQ == _('Unknown') \
                                or (hw.Card.IRQ == 'Unknown')):
                            continue
                        dic = modules[hw.Card.ModuleName]
                        if not dic.has_key('options'):
                            dic['options'] = {}
                        dic['options'][confkey] = str(hw.Card.__dict__[selfkey])
                        modules[hw.Card.ModuleName] = dic


            if hw.Type == MODEM and hw.Modem:
                if not wvdial:
                    wvdial = ConfSMB('/etc/wvdial.conf', create_if_missing = true)
                wvdial[hw.Name]['Modem'] = hw.Modem.DeviceName
                wvdial[hw.Name]['Baud'] = str(hw.Modem.BaudRate)
                wvdial[hw.Name]['SetVolume'] = str(hw.Modem.ModemVolume)
                wvdial[hw.Name]['Dial Command'] = str(hw.Modem.DialCommand)
                if not hw.Modem.InitString: hw.Modem.InitString = 'ATZ'
                wvdial[hw.Name]['Init1'] = str(hw.Modem.InitString)
                wvdial[hw.Name]['FlowControl'] = str(hw.Modem.FlowControl)

            if hw.Type == ISDN:
                isdn.Description = hw.Description
                isdn.Type = hw.Card.Type
                isdn.ModuleName = hw.Card.ModuleName
                isdn.IRQ = hw.Card.IRQ
                isdn.IoPort = hw.Card.IoPort
                isdn.IoPort1 = hw.Card.IoPort1
                isdn.IoPort2 = hw.Card.IoPort2
                isdn.Mem = hw.Card.Mem
                isdn.ChannelProtocol = hw.Card.ChannelProtocol
                isdn.Firmware = hw.Card.Firmware
                isdn.DriverId = hw.Card.DriverId
                isdn.VendorId = hw.Card.VendorId
                isdn.DeviceId = hw.Card.DeviceId

        if wvdial:
            # Clean up wvdial
            for dev in wvdial.keys():
                if dev[:5] != 'Modem':
                    continue
                for hw in self:
                    if hw.Type == MODEM and hw.Name == dev:
                        break
                else:
                    # if the loop does not get interrupted by break
                    # we did not find the Modem in the hardwarelist
                    # and it gets deleted
                    del wvdial[dev]
                    
        # Clean up modules
        for mod in modules.keys():
            type = getDeviceType(mod)
            if type != 'Ethernet':
                continue
            #print "Testing " + str(mod)
            for hw in self:
                if hw.Type == ETHERNET and hw.Name == mod:
                    break
            else:
                #print "Removing " + str(mod)
                #print str(modules.vars[mod].keys())
                del modules[mod]
                #print "Test: " + str(modules[mod])
                
        modules.write()
        if wvdial:
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
