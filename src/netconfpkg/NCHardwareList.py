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
    if ModInfo == None:
#         ModInfo = {}
#         for mod in __networkmodulelist:
#             if mod.find(".ko") != -1:
#                 i = mod.find(".ko")
#                 mod = mod[:i]

#             try:
#                 desc = execWithCapture("/sbin/modinfo", [ "/sbin/modinfo", "-F", "description", mod ])
#                 ModInfo[mod] = {}
#                 ModInfo[mod]['type'] = 'eth'
#                 ModInfo[mod]['description'] = desc.strip()
#             except:
#                 pass
            
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
    s390devs = { "ctc" : "ctc",
                 "escon" : "ctc",
                 "lcs" : "lcs" ,
                 "osad" : "",
                 "iucv" : "iucv",
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
        return i

    def updateFromChandev(self):
        machine = os.uname()[4]
        if machine != 's390' and machine != 's390x' and not getDebugLevel():
            return

        procfilename = "/proc/chandev"
        try:
            conf = file(procfilename, "r")
        except:
            return

        detect_state = None

        for line in conf:
            line.strip()

            if not detect_state:
                if line.find("Initialised Devices") >= 0:
                    detect_state = 1
                else:
                    continue
            else:
                if line == "":
                    detect_state = None
                    continue

                if len(line) <= 2:
                    continue

                if line[:2] != "0x":
                    continue

                toks = line.split()

                if len(toks) < 11:
                    continue

                device = None
                dev = toks[9]
                for d in HardwareList.s390devs.keys():
                    if len(dev) <= len(d):
                        continue
                    if dev[:len(d)] != d:
                        continue
                    device = dev
                    break
                for i in xrange(len(toks)):
                    if toks[i] == "n/a":
                        toks[i] = 0

                if device:
                    for hw in self:
                        if hw.Name == device:
                            #hw.Status = HW_OK
                            break
                    else:
                        type = getDeviceType(device)
                        i = self.addHardware(type)
                        hw = self[i]
                        hw.createCard()
                        hw.Name = device
                        hw.Type = type
                        hw.Card.IoPort = toks[3]
                        hw.Card.IoPort1 = toks[4]
                        hw.Card.IoPort2 = toks[5]
                        if HardwareList.s390devs.has_key(device):
                            hw.Card.ModuleName = HardwareList.s390devs[device]
                        hw.Status = HW_SYSTEM


    def readChandev(self):
        machine = os.uname()[4]
        if machine != 's390' and machine != 's390x' and not getDebugLevel():
            return

        conffilename = getRoot() + "/etc/chandev.conf"
        try:
            conf = file(conffilename, "r")
        except:
            return

        for line in conf:

            line.strip()
            try:
                if len(line) and line[-1] == '\n':
                    line = line[:-1]
                if len(line) and line[-1] == '\r':
                    line = line[:-1]
            except: pass

            toks = line.split(",")
            device = None
            if len(toks):
                # Check for Device line
                dev = toks[0]
                for d in HardwareList.s390devs.keys():
                    if len(dev) <= len(d):
                        continue
                    if dev[:len(d)] != d:
                        continue
                    device = dev
                    break

                # Check for add_parms
                #if toks[0] == "add_parms":
                #print "extra parms %s" % string.join(toks[1:])

                if not device:
                    continue

            type = getDeviceType(device)
            i = self.addHardware(type)
            hw = self[i]
            hw.createCard()
            hw.Name = device
            hw.Type = type
            if not hw.Description: hw.Description = type
            hw.Description += " " + string.join(toks[1:], ",")
            if len(toks) >= 2:
                hw.Card.IoPort = toks[1]
                if len(toks) >= 3:
                    hw.Card.IoPort1 = toks[2]
                    if len(toks) >= 4:
                        hw.Card.IoPort2 = toks[3]
            if HardwareList.s390devs.has_key(device):
                hw.Card.ModuleName = HardwareList.s390devs[device]
            hw.Status = HW_CONF

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
                hw.setChanged(True)

        for h in hdellist:
            log.log(5, "Removing %s from HWList" % h.Name)
            self.remove(h)

        del hdellist
        

    def updateFromSys(self, hdellist):
        import glob
        import os

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
                        i = self.addHardware(getDeviceType(device))
                        hw = self[i]
                        hw.Name = device
                        hw.Description = mod
                        hw.Status = HW_SYSTEM
                        hw.Type = getDeviceType(device)
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
                    self.append(hw)
                    hw.Status = HW_SYSTEM
                    hw.setChanged(True)        

        return hdellist

    def updateFromSystem(self):
        log.log(5, "updateFromSystem")
        try:
            self.updateFromKudzu()
        except:
            pass

        log.log(5, "updateFromKudzu")
        log.log(5, str(self))

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

        self.readChandev()
        # FIXME: move HW detection to NCDev*
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
__date__ = "$Date: 2007/07/13 12:31:36 $"
__version__ = "$Revision: 1.84 $"
