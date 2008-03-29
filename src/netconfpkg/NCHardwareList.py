## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
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

from netconfpkg.conf.Conf import *
from netconfpkg.conf.ConfSMB import *
from rhpl.executil import *

ModInfo = None
__isdnmodulelist = []
try:
    __msg =  execWithCapture("/bin/sh", [ "/bin/sh", "-c", "find /lib/modules/$(uname -r)/*/drivers/isdn -name '*.?o' -printf '%f ' 2>/dev/null" ])
    __isdnmodulelist = string.split(__msg)
except:
    pass

__wirelessmodulelist = []
try:
    __msg =  execWithCapture("/bin/sh", [ "/bin/sh", "-c", "find /lib/modules/$(uname -r)/*/drivers/net/wireless -name '*.?o' -printf '%f ' 2>/dev/null" ])
    __wirelessmodulelist = string.split(__msg)
except:
    pass


#__networkmodulelist = []
#try:
#    __msg =  execWithCapture("/bin/sh", [ "/bin/sh", "-c", "find /lib/modules/$(uname -r)/*/drivers/net -name '*.?o' -printf '%f ' 2>/dev/null" ])
#    __networkmodulelist.append(__isdnmodulelist)
#    __networkmodulelist = string.split(__msg)
#except:
#    pass


def getModInfo():
    global ModInfo
    
    if getTestEnv():
        return None
    
    if ModInfo == None:            
        for path in [ '/boot/module-info',
                   NETCONFDIR + '/module-info',
                   './module-info' ]:
            try:
                ModInfo = ConfModInfo(filename = path)
            except (VersionMismatch, FileMissing):
                continue
            break

    return ModInfo

class MyConfModules(ConfModules):
    def __init__(self, filename = None):
        # if we put getRoot() in the default parameter it will
        # have the value at parsing time
        if filename == None:
            filename = getRoot() + MODULESCONF
        # FIXME: [187640] Support aliases in /etc/modprobe.d/
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


    def splitopt(self, opt):
        eq = find(opt, '=')
        if eq > 0:
            return (opt[:eq], opt[eq+1:])
        else:
            return (opt, None)

    def joinoptlist(self, dict):
        optstring = ''
        for key in dict.keys():
            if dict[key] != None:
                optstring = optstring + key + '=' + dict[key] + ' '
            else:
                optstring = optstring + key + ' '

        return optstring



_MyConfModules = None
_MyConfModules_root = getRoot()

def getMyConfModules(refresh = None):
    global _MyConfModules
    global _MyConfModules_root

    if _MyConfModules == None or refresh or \
           _MyConfModules_root != getRoot() :
        _MyConfModules = MyConfModules()
        _MyConfModules_root = getRoot()
    return _MyConfModules

_MyWvDial = None
_MyWvDial_root = getRoot()

def getMyWvDial(create_if_missing = None):
    global _MyWvDial
    global _MyWvDial_root

    if _MyWvDial == None or _MyWvDial_root != getRoot():
        _MyWvDial = ConfSMB(getRoot() + WVDIALCONF,
                           create_if_missing = create_if_missing)
        _MyWvDial_root = getRoot()

    return _MyWvDial

class ConfHWConf(Conf): 
    # pylint: disable-msg=W0233,W0231

    def __init__(self):
        Conf.__init__(self, getRoot() + HWCONF)

    def read(self):
        Conf.read(self)
        self.initvars()

    def initvars(self):
        self.vars = {}

        if not os.access(getRoot() + HWCONF, os.R_OK):
            return

        fp = open(getRoot() + HWCONF, 'r')
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
    s390devs = { 
                 "lcs" : "lcs" ,
                 "osad" : "",
                 "eth" : "qeth",
                 "hsi" : "qeth",
                 "tr" : "qeth",
                 }

    def __init__(self, list = None, parent = None):
        HardwareList_base.__init__(self, list, parent)
        # FIXME: [198070] use modinfo to determine options
        self.keydict = { }

    def addHardware(self, type = None):
        from netconfpkg.NCHardwareFactory import getHardwareFactory
        i = HardwareList_base.addHardware(self)
        hwf = getHardwareFactory()
        hwc = hwf.getHardwareClass(type)
        if hwc:
            newhw = hwc()
            self[i] = newhw
#        else: # FIXME: !!
#            raise TypeError
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
                if (kudzu_device.driver + '.o' in __isdnmodulelist) or \
                       (kudzu_device.driver + '.ko' in __isdnmodulelist) :
                    kudzu_device.device = ISDN
                elif (kudzu_device.driver + '.o' in __wirelessmodulelist) or \
                         (kudzu_device.driver + '.ko' in __wirelessmodulelist):
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

                log.log(5, "Found %s in ethlist" % dev)
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
                    log.log(5, "Found nothing for %s" % str(kudzu_device))
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

            log.log(5, "Found dev %s - %s" % (dev, module))
            # if it is already in our HW list do not delete it.
            for h in hdellist:
                if h.Name == dev and h.Card.ModuleName == module:
                    hdellist.remove(h)
                    break
            else:            
                hwtype = getDeviceType(dev, module = module)
                i = self.addHardware(hwtype)
                hw = self[i]
                if string.find (kudzu_device.desc, "|") != -1:
                    mfg, desc = string.split (kudzu_device.desc, "|")
                else:
                    mfg = _("Unknown")
                    desc = kudzu_device.desc

                hw.Name = dev
                hw.Type = hwtype
                hw.Description = desc
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
                hw.setChanged(True)

        for h in hdellist:
            log.log(5, "Removing %s from HWList" % h.Name)
            self.remove(h)

        del hdellist
        

    def updateFromSys(self, hdellist):
        import glob

        modules = getMyConfModules()
        modinfo = getModInfo()            
        #
        # Read in actual system state
        #
        for syspath in glob.glob('/sys/class/net/*'):
            device = os.path.basename(syspath)
            mod = None
            try:                
                mod = os.path.basename(os.readlink('%s/device/driver' % syspath))
            except:                
                pass

            try:
                fp = open("%s/type" % syspath)
                line = fp.readlines()
                fp.close()
                line = string.join(line)
                line.strip()
                log.log(5, "type %s = %s" % (device, line))
                type = int(line)
                if type >= 256:
                    continue
            except:
                pass

            log.log(5, "%s = %s" % (device, mod))
            
            h = None
            for h in self:
                if h.Name == device:
                    break

            if h and h.Name == device and h.Status != HW_SYSTEM:
                continue

#            if device[:3] != "eth":
#                continue

            # No Alias devices
            if string.find(device, ':') != -1:
                continue

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
                    for h in self:
                        if h.Name == device and h.Card.ModuleName == mod:
                            break
                    else:
                        hwtype = getDeviceType(device, module = mod)
                        i = self.addHardware(hwtype)
                        hw = self[i]
                        hw.Name = device
                        hw.Description = mod
                        hw.Status = HW_SYSTEM
                        hw.Type = hwtype
                        hw.createCard()
                        hw.Card.ModuleName = mod
                        if modinfo:
                            for info in modinfo.keys():
                                if info == mod:
                                    if modinfo[info].has_key('description'):
                                        hw.Description = \
                                            modinfo[info]['description']

                        for selfkey in self.keydict.keys():
                            confkey = self.keydict[selfkey]
                            if modules[hw.Card.ModuleName] and \
                                    modules[hw.Card.ModuleName]\
                                    ['options'].has_key(confkey):
                                hw.Card.__dict__[selfkey] = modules[hw.Card.\
                                                                        ModuleName]\
                                                                        ['options']\
                                                                        [confkey]
                        hw.setChanged(True)

        return hdellist


    def updateFromHal(self, hdellist):
        import NCBackendHal
        hal = NCBackendHal.NCBackendHal()
        cards = hal.probeCards()
        for hw in cards:
            # if it is already in our HW list do not delete it.
            for h in hdellist:
                if h.Name == hw.Name and h.Card.ModuleName == hw.Card.ModuleName:
                    log.log(5, "Found %s:%s, which is already in our list!" % (hw.Name, hw.Card.ModuleName))
                    hdellist.remove(h)
                    break
                else:
                    log.log(5, "%s != %s and %s != %s" % (h.Name, hw.Name, h.Card.ModuleName, hw.Card.ModuleName))
            else: 
                for h in self:
                    if h.Name == hw.Name and h.Card.ModuleName == hw.Card.ModuleName:
                        break
                    else:
                        log.log(5, "%s != %s and %s != %s" % (h.Name, hw.Name, h.Card.ModuleName, hw.Card.ModuleName))
                else:
                    hw.Status = HW_SYSTEM
                    self.append(hw)
                    hw.setChanged(True)        

        return hdellist

    def updateFromSystem(self):
        log.log(5, "updateFromSystem")
        
        
#        log.log(5, "updateFromKudzu")
#        try:
#            self.updateFromKudzu()
#        except:
#            pass
#        log.log(5, str(self))

        hdellist = []

        for h in self:
            if h.Status == HW_SYSTEM:
                hdellist.append(h)

        try:
            self.updateFromChandev()
        except:
            pass


        try:
            hdellist = self.updateFromHal(hdellist)
        except:
            pass

        log.log(5, "updateFromHal")
        log.log(5, str(self))

        try:
            hdellist = self.updateFromSys(hdellist)
        except:
            pass


        log.log(5, "updateFromSys")
        log.log(5, str(self))

        for h in hdellist:
            log.log(5, "Removing %s from HWList" % h.Name)
            self.remove(h)

        del hdellist

        log.log(5, str(self))

    def updateFromModules(self):
        modules = getMyConfModules()
        modinfo = getModInfo()
        #
        # Read /etc/modprobe.conf
        #
        for mod in modules.keys():
            if modules[mod].has_key('alias'):
                module = modules[mod]['alias']
            else: module = None

            type = getDeviceType(mod, module)

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
            if module and modinfo:
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

        # FIXME: move HW detection to NCDev*
        import netconfpkg
        dosysupdate=True
        if getTestEnv():
            dosysupdate=False
        if dosysupdate:
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
        # FIXME: This is not OO!
        #
        try:
            wvdial = ConfSMB(getRoot() + WVDIALCONF)
        except FileMissing:
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
                try:
                    hw.Modem.BaudRate = int(wvdial[dev]['Baud'])
                except ValueError:
                    hw.Modem.BaudRate = 38400

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

        self.commit(changed=False)
        self.setChanged(False)

    def save(self):
        self.commit(changed=True)

        modules = getMyConfModules(refresh = True)

        # cleanup isdnconf
        isdn = NCisdnhardware.ConfISDN()
        isdn.cleanup()

        for hw in self:
            hw.save()

        try:
            wvdial = getMyWvDial(create_if_missing = False)
        except:
            wvdial = None
            pass

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

        # FIXME: [198070] use modinfo to determine options
        # Clean up modules
        for mod in modules.keys():
            type = getDeviceType(mod)
            #
            # FIXME: This is not OO!!
            #
            if type != ETHERNET and type != TOKENRING and type != QETH:
                continue
            #print "Testing " + str(mod)
            for hw in self:
                if (hw.Type == ETHERNET or \
                    hw.Type == TOKENRING or hw.Type == QETH) and \
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

        self.commit(changed=False)
        self.setChanged(False)

__HWList = None
__HWList_root = getRoot()

def getHardwareList(refresh = None):
    global __HWList
    global __HWList_root

    if __HWList == None or refresh or \
           __HWList_root != getRoot():
        __HWList = HardwareList()
        __HWList.load()
        __HWList_root = getRoot()
    return __HWList

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

__author__ = "Harald Hoyer <harald@redhat.com>"
