## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
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
from netconfpkg.NCHardware import *
from NC_functions import *

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

from rhpl.Conf import *
from rhpl.ConfSMB import *
from rhpl.executil import *

ModInfo = None
isdnmodulelist = []
try:
    msg =  execWithCapture("/bin/sh", [ "/bin/sh", "-c", "find /lib/modules/$(uname -r)/kernel/drivers/isdn -name \*.o -printf '%f '" ])
    isdnmodulelist = string.split(msg)
except:
    pass

wirelessmodulelist = []
try:
    msg =  execWithCapture("/bin/sh", [ "/bin/sh", "-c", "find /lib/modules/$(uname -r)/kernel/drivers/net/wireless -name \*.o -printf '%f '" ])
    wirelessmodulelist = string.split(msg)
except:
    pass

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
    def __init__(self, filename = None):
        # if we put netconfpkg.ROOT in the default parameter it will
        # have the value at parsing time
        if filename == None:
            filename = netconfpkg.ROOT + MODULESCONF
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
        log.ldel(2, self.filename, varname)
        self.seek(place)
        
_MyConfModules = None
def getMyConfModules(refresh = None):
    global _MyConfModules
    if _MyConfModules == None or refresh:
        _MyConfModules = MyConfModules()
    return _MyConfModules

        
class ConfHWConf(Conf):
    def __init__(self):
        Conf.__init__(self, netconfpkg.ROOT + HWCONF)

    def read(self):
        Conf.read(self)
        self.initvars()

    def initvars(self):
        self.vars = {}

        if not os.access(netconfpkg.ROOT + HWCONF, os.R_OK):
            return

        fp = open(netconfpkg.ROOT + HWCONF, 'r')
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

    def updateFromKudzu(self):
        import kudzu
        modules = getMyConfModules()
        ethlist = ethtool.get_devices()

        hdellist = []
        for h in self:
            if h.Status == HW_OK:
                hdellist.append(h)
                
        #
        # Read from kudzu
        #
        kudzulist = []
        kudzulist.extend(kudzu.probe(kudzu.CLASS_NETWORK, kudzu.BUS_UNSPEC,
                                     kudzu.PROBE_SAFE))
        for kudzu_device in kudzulist:
            if not kudzu_device.device and kudzu_device.driver:
                if kudzu_device.driver + '.o' in isdnmodulelist:
                    kudzu_device.device = ISDN
                elif kudzu_device.driver + '.o' in wirelessmodulelist:
                    kudzu_device.device = WIRELESS

            if not kudzu_device.device:
                continue

            if (kudzu_device.driver == "ignore"):
                continue

            log.log(3, "Checking %s " % str(kudzu_device))

            l = len(kudzu_device.device)

            # ok, first try the actual system state
            for dev in ethlist:
                if dev[:l] != kudzu_device.device:
                    continue

                # No Alias devices
                if string.find(dev, ':') != -1:
                    continue

                try:
                    module = ethtool.get_module(dev)
                except IOError, err:
                    module = None

                if not module:
                    continue

                if not kudzu_device.driver:
                    continue
                
                if module != kudzu_device.driver:
                    log.log(3, "Error... kudzu != actual system state")

                log.log(3, "Found %s in ethlist" % dev)
                ethlist.remove(dev)

                break
            else:
                # Now try modules.conf
                for dev in modules.keys():
                    if dev[:l] != kudzu_device.device:
                        continue

                    if modules[dev].has_key('alias'):
                        module = modules[dev]['alias']
                    else:
                        continue
                    break
                else:
                    log.log(3, "Found nothing for %s" % str(kudzu_device))
                    dev = kudzu_device.device
                    # ok, now search for an empty slot
                    for num in xrange(0,20):
                        for h in self:
                            if h.Name == dev + str(num):
                                break
                        else:
                            # no card seems to use this 
                            dev = dev + str(num)
                        break
                    break

            log.log(3, "Found dev %s - %s" % (dev, module))
            # if it is already in our HW list do not delete it.
            for h in hdellist:
                if h.Name == dev and h.Card.ModuleName == module:
                    hdellist.remove(h)
                    break
            else:            
                i = self.addHardware(getDeviceType(dev))
                hw = self[i]
                if string.find (kudzu_device.desc, "|") != -1:
                    mfg, desc = string.split (kudzu_device.desc, "|")
                else:
                    mfg = _("Unknown")
                    desc = kudzu_device.desc

                hw.Name = dev

                hw.Description = desc
                hw.Type = getDeviceType(dev)
                hw.Status = HW_OK
                hw.createCard()
                hw.Card.ModuleName = module

                for selfkey in self.keydict.keys():
                    confkey = self.keydict[selfkey]
                    if modules[hw.Card.ModuleName] and \
                           modules[hw.Card.ModuleName]['options'].\
                           has_key(confkey):
                        hw.Card.__dict__[selfkey] = modules[\
                               hw.Card.ModuleName]['options'][confkey]
                hw.setChanged(true)

        for h in hdellist:
            log.log(5, "Removing %s from HWList" % h.Name)
            self.remove(h)

        del hdellist


    def updateFromSystem(self):
        modules = getMyConfModules()
        modinfo = getModInfo()            

        self.updateFromKudzu()

        hdellist = []
        
        for h in self:
            if h.Status == HW_SYSTEM:
                hdellist.append(h)
                
        #
        # Read in actual system state
        #
        for device in ethtool.get_devices():
	    h = None
            for h in self:
                if h.Name == device:
                    break

            if h and h.Name == device and h.Status != HW_SYSTEM:
                continue

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
                # if it is already in our HW list do not delete it.
                for h in hdellist:
                    if h.Name == device and h.Card.ModuleName == mod:
                        log.log(5, "Found %s:%s, which is already in our list!" % (device, mod))
                        hdellist.remove(h)
                        break
                    else:
                        log.log(5, "%s != %s and %s != %s" % (h.Name, device, h.Card.ModuleName, mod))
                else:
                    i = self.addHardware(getDeviceType(device))
                    hw = self[i]
                    hw.Name = device
                    hw.Description = mod
                    hw.Status = HW_SYSTEM
                    hw.Type = getDeviceType(device)                        
                    hw.createCard()
                    hw.Card.ModuleName = mod
                    for info in modinfo.keys():
                        if info == mod:
                            if modinfo[info].has_key('description'):
                                hw.Description = modinfo[info]['description']

                    for selfkey in self.keydict.keys():
                        confkey = self.keydict[selfkey]
                        if modules[hw.Card.ModuleName] and \
                               modules[hw.Card.ModuleName]\
                               ['options'].has_key(confkey):
                            hw.Card.__dict__[selfkey] = modules[hw.Card.\
                                                                ModuleName]\
                                                                ['options']\
                                                                [confkey]
                    hw.setChanged(true)

        for h in hdellist:
            log.log(5, "Removing %s from HWList" % h.Name)
            self.remove(h)

        del hdellist


    def updateFromModules(self):
        modules = getMyConfModules()
        modinfo = getModInfo()
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

            h = None
            for h in self:
                if h.Name == mod:
                    break
            
            if h and h.Name == mod:
                continue
             
            i = self.addHardware(type)
            hw = self[i]
            hw.Name = mod
            hw.Description = module
            hw.Type = type
            hw.createCard()
            hw.Card.ModuleName = module
            hw.Status = HW_CONF
            if module:
                for info in modinfo.keys():
                    if info == module:
                        if modinfo[info].has_key('description'):
                            hw.Description = modinfo[info]['description']
                            
            for selfkey in self.keydict.keys():
                confkey = self.keydict[selfkey]
                if modules[hw.Card.ModuleName] and \
                       modules[hw.Card.ModuleName]['options'].has_key(confkey):
                    hw.Card.__dict__[selfkey] = modules[hw.Card.ModuleName]\
                                                ['options'][confkey]


    def _objToStr(self, parentStr = None):
        #return DeviceList_base._objToStr(self, obj, parentStr)
        retstr = ""
        for dev in self:
            retstr += dev._objToStr("HardwareList.%s.%s" % (dev.Type,
                                                            dev.Name))

        return retstr


    def _parseLine(self, vals, value):
        class BadLineException: pass
        if len(vals) <= 1:
            return
        if vals[0] == "HardwareList":
            del vals[0]
        else:
            return
        for dev in self:
            if dev.Name == vals[1]:
                if dev.Type != vals[0]:
                    self.remove(dev)
                    log.log(1, "Deleting device %s" % vals[1] )
                    break
                dev._parseLine(vals[2:], value)
                return
        log.log(4, "Type = %s, Name = %s" % (vals[0], vals[1]))
        i = self.addHardware(vals[0])
        dev = self[i]
        dev.Name = vals[1]
        dev._parseLine(vals[2:], value)


    def load(self):
        hwconf = ConfHWConf()          

	# first clear the list
        self.__delslice__(0, len(self))
        
        self.updateFromSystem()        
        self.updateFromModules()

        for hw in self:
            if hw.Name == "ISDN Card 0":
                break
        else:
            #
            # XXX FIXME... this is not OO
            #
            isdncard = NCisdnhardware.ConfISDN()
            if isdncard.load() > 0:
                i = self.addHardware(ISDN)
                hw = self[i]
                hw.Name = "ISDN Card 0"
                hw.Description = isdncard.Description
                hw.Type = ISDN
                hw.Status = HW_CONF
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
            
        #
        # XXX FIXME... this is not OO
        #
        try:
            wvdial = ConfSMB(netconfpkg.ROOT + WVDIALCONF)
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
                hw.Status = HW_CONF
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
        #self.updateFromSystem()

    def save(self):
        modules = getMyConfModules(refresh = true)
        if not os.access(netconfpkg.ROOT + WVDIALCONF, os.R_OK):
            wvdial  = None
        else:
            wvdial = ConfSMB(netconfpkg.ROOT + WVDIALCONF)

        isdn = NCisdnhardware.ConfISDN()
        

        for hw in self:
            #
            # XXX FIXME... this is not OO
            #
            if hw.Type == ETHERNET:
                dic = modules[hw.Name]
                dic['alias'] = hw.Card.ModuleName
                modules[hw.Name] = dic
                log.lch(2, modules.filename, "%s alias %s" % (hw.Name, hw.Card.ModuleName))
                # No, no, no... only delete known options!!!
                #WRONG: modules[hw.Card.ModuleName] = {}
                #WRONG: modules[hw.Card.ModuleName]['options'] = {}
                #
                # Better do it this way!
                if modules[hw.Card.ModuleName].has_key('options'):
                    for (key, confkey) in self.keydict.items():
                        if modules[hw.Card.ModuleName]\
                               ['options'].has_key(confkey):
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
                        dic['options'][confkey] = \
                                                str(hw.Card.__dict__[selfkey])
                        modules[hw.Card.ModuleName] = dic


            #
            # XXX FIXME... this is not OO
            #
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
                        if modules[hw.Card.ModuleName]\
                               ['options'].has_key(confkey):
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
                        dic['options'][confkey] = \
                                                str(hw.Card.__dict__[selfkey])
                        modules[hw.Card.ModuleName] = dic


            #
            # XXX FIXME... this is not OO
            #
            if hw.Type == MODEM and hw.Modem:
                if not wvdial:
                    wvdial = ConfSMB(netconfpkg.ROOT + WVDIALCONF,
                                     create_if_missing = true)
                wvdial[hw.Name]['Modem'] = hw.Modem.DeviceName
                wvdial[hw.Name]['Baud'] = str(hw.Modem.BaudRate)
                wvdial[hw.Name]['SetVolume'] = str(hw.Modem.ModemVolume)
                wvdial[hw.Name]['Dial Command'] = str(hw.Modem.DialCommand)
                if not hw.Modem.InitString: hw.Modem.InitString = 'ATZ'
                wvdial[hw.Name]['Init1'] = str(hw.Modem.InitString)
                wvdial[hw.Name]['Init3'] = 'ATM' + str(hw.Modem.ModemVolume)
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
            #
            # XXX FIXME... this is not OO
            #
            if type != ETHERNET and type != TOKENRING:
                continue
            #print "Testing " + str(mod)
            for hw in self:
                if (hw.Type == ETHERNET or \
                    hw.Type == TOKENRING) and \
                    hw.Name == mod:
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

def getHardwareList(refresh = None):
    global HWList
    if HWList == None or refresh:
        HWList = HardwareList()
        HWList.load()
    return HWList

def getNextDev(base):
    hwlist = getHardwareList()
    num = 0
    for num in xrange(0,100):
        for hw in hwlist:
            if hw.Name == base + str(num):
                break
        else:
            # no card seems to use this                         
            break
        
    return base + str(num)


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
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/05/16 09:45:00 $"
__version__ = "$Revision: 1.69 $"
