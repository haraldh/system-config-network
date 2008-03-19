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

import os
import os.path
import re
from netconfpkg.NC_functions import _, log, ConfDevices, \
    generic_longinfo_dialog, getDeviceType, \
    getRoot, OLDSYSCONFDEVICEDIR, QETH, SYSCONFDEVICEDIR, \
    updateNetworkScripts, getCHAPConf, getPAPConf, IPSEC, \
    SYSCONFNETWORK, testFilename, unlink, WVDIALCONF
from netconfpkg import DeviceList_base # pylint: disable-msg=E0611
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.conf import ConfSMB
from netconfpkg.conf import Conf

class DeviceList(DeviceList_base):
    def __init__(self, clist = None, parent = None):
        DeviceList_base.__init__(self, clist, parent)


    def load(self):
        from netconfpkg.NCDevice import ConfDevice
        updateNetworkScripts()

        self.__delslice__(0, len(self)) # pylint: disable-msg=E1101

        df = getDeviceFactory()
        devdir = getRoot() + SYSCONFDEVICEDIR
        devices = []
        
        log.log(5, "Checking %s" % devdir)
        if os.path.isdir(devdir):
            devices = ConfDevices()
            
        if not devices:
            log.log(5, "Checking %s" % devdir)
            devdir = getRoot() + OLDSYSCONFDEVICEDIR
            devices = ConfDevices(devdir)

        for dev in devices:
            log.log(5, "Checking %s" % dev)
            if dev == 'lo':
                continue
            conf = ConfDevice(dev, devdir)
            mtype = None
            device = None
            # take a peek in the config file
            if conf.has_key("TYPE"):
                mtype = conf["TYPE"]
            if conf.has_key("DEVICE"):
                device = conf["DEVICE"]
            if conf.has_key("NETTYPE"):
                if conf["NETTYPE"] == "qeth":
                    mtype = QETH

            del conf

            if mtype == "IPSEC":
                continue

            if not mtype or mtype == "" or mtype == _("Unknown"):
                from netconfpkg import NCHardwareList
                hwlist = NCHardwareList.getHardwareList()
                for hw in hwlist:
                    if hw.Name == device:
                        mtype = hw.Type
                        break
                else:
                    mtype = getDeviceType(device)

            devclass = df.getDeviceClass(mtype)
            if devclass:
                newdev = devclass()
                newdev.load(dev)
                self.append(newdev) # pylint: disable-msg=E1101
                
#                try:
#                    newdev.load(dev)
#                except BaseException, e:
#                    # FIXME: better exception handling
#                    generic_error_dialog (_("Error loading file %s\n%s") % (devdir + "/ifcfg-" + dev, str(e)), 
#                                          dialog_type="error")
#                else:
#                    self.append(newdev) # pylint: disable-msg=E1101
                    
            else:
                log.log(1, "NO DEVICE CLASS FOUND FOR %s" % dev)
                i = self.addDevice() # pylint: disable-msg=E1101
                self[i].load(dev)

        self.commit(False) # pylint: disable-msg=E1101
        self.setChanged(False) # pylint: disable-msg=E1101

        chdev = {}
        # the initscripts do not like '-'
        for dev in self:
            newDeviceId = re.sub('-', '_', dev.DeviceId)
            if newDeviceId != dev.DeviceId:
                chdev[dev.DeviceId] = newDeviceId
                #log.log(4, "%s != %s" % (newDeviceId, dev.DeviceId))
                # Fixed change device names in active list of all profiles
                import netconfpkg.NCProfileList
                profilelist = netconfpkg.NCProfileList.getProfileList()

                for prof in profilelist:
                    #log.log(4, str(prof.ActiveDevices))
                    if dev.DeviceId in prof.ActiveDevices:
                        pos = prof.ActiveDevices.index(dev.DeviceId)
                        prof.ActiveDevices[pos] = newDeviceId
                        #log.log(4, "changed %s" % (prof.ActiveDevices[pos]))
                        #log.log(4, str(prof.ActiveDevices))
                        prof.commit()

                dev.DeviceId = newDeviceId
                dev.commit(changed=False)
                dev.setChanged(False)

        if len(chdev.keys()):
            s =_("Changed the following Nicknames due to the initscripts:\n")
            for n, d in chdev.items():
                s += "%s -> %s\n" % (n, d)
            generic_longinfo_dialog(_("Nicknames changed"), s)


    def addDeviceType(self, mtype):
        df = getDeviceFactory()
        devclass = df.getDeviceClass(mtype)
        i = self.addDevice() # pylint: disable-msg=E1101
        if devclass:
            newdev = devclass()
            self[i] = newdev
        return self[i]

    def test(self):
        pass

    def __repr__(self):
        return repr(self.__dict__)

    def _objToStr(self, parentStr = None): # pylint: disable-msg=W0613
        #return DeviceList_base._objToStr(self, obj, parentStr)
        retstr = ""
        for dev in self:
            # pylint: disable-msg=W0212
            retstr += dev._objToStr("DeviceList.%s.%s" % (dev.Type,
                                                          dev.DeviceId))

        return retstr


    def _parseLine(self, vals, value):
        if len(vals) <= 1:
            return
        if vals[0] == "DeviceList":
            del vals[0]
        else:
            return
        for dev in self:
            if dev.DeviceId == vals[1]:
                if dev.Type != vals[0]:                    
                    self.pop(dev) # pylint: disable-msg=E1101
                    log.log(1, "Deleting device %s" % vals[1] )
                    break
                dev._parseLine(vals[2:], value) # pylint: disable-msg=W0212
                return

        dev = self.addDeviceType(vals[0])
        dev.DeviceId = vals[1]
        dev._parseLine(vals[2:], value) # pylint: disable-msg=W0212

    def save(self):
        # FIXME: [163040] "Exception Occurred" when saving
        # fail gracefully, with informing, which file, and why

        from netconfpkg.NCDevice import ConfDevice
        from types import DictType
        
        self.commit(changed=True) # pylint: disable-msg=E1101

        nwconf = Conf.ConfShellVar(getRoot() + SYSCONFNETWORK)
        if len(self) > 0:
            nwconf["NETWORKING"] = "yes"
        nwconf.write()

        #
        # clear all Dialer sections in wvdial.conf
        # before the new Dialer sections written
        #
        wvdialconf = ConfSMB.ConfSMB(filename = getRoot() + WVDIALCONF)
        for wvdialkey in wvdialconf.vars.keys():
            if wvdialkey[:6] == 'Dialer':
                del wvdialconf[wvdialkey]
        wvdialconf.write()

        #
        # Clear all pap and chap-secrets generated by netconf
        #
        papconf = getPAPConf()
        chapconf = getCHAPConf()
        for key in papconf.keys():
            if isinstance(papconf[key], DictType):
                for server in papconf[key].keys():
                    papconf.delallitem([key, server])
            del papconf[key]
        for key in chapconf.keys():
            if isinstance(chapconf[key], DictType):
                for server in chapconf[key].keys():
                    chapconf.delallitem([key, server])
            del chapconf[key]

        #
        # traverse all devices in the list
        #
        for dev in self:
            #
            # really save the device
            #
            #if dev.changed:
            dev.save()

        papconf.write()
        chapconf.write()

        dirname = getRoot() + SYSCONFDEVICEDIR
        #
        # Remove old config files
        #
        try:
            mdir = os.listdir(dirname)
        except OSError, msg:
            raise IOError, 'Cannot save in ' \
                  + dirname + ': ' + str(msg)

        for entry in mdir:
            if not testFilename(dirname + entry):
                log.log(5, "not testFilename(%s)" % (dirname + entry))
                continue

            if (len(entry) <= 6) or \
                   entry[:6] != 'ifcfg-':
                log.log(5, "not ifcfg %s" % (entry))
                continue

            devid = entry[6:]
            for dev in self:
                if dev.DeviceId == devid:
                    break
            else:
                # check for IPSEC
                conf = ConfDevice(devid, dir=dirname)
                mtype = IPSEC
                if conf.has_key("TYPE"):
                    mtype = conf["TYPE"]

                if mtype == IPSEC:
                    log.log(5, "IPSEC %s" % (entry))
                    continue

                # now remove the file
                unlink(dirname + entry)
                unlink(getRoot() + OLDSYSCONFDEVICEDIR + \
                       '/ifcfg-' + devid)

        # remove old route files
        for entry in mdir:
            if not testFilename(dirname + entry):
                continue

            if (len(entry) <= 6) or \
                   entry[:6] != '.route':
                continue

            devid = entry[6:]

            for dev in self:
                if dev.DeviceId == devid:
                    break
            else:
                # remove route file, if no routes defined
                unlink(dirname + entry)
                unlink(getRoot() + OLDSYSCONFDEVICEDIR + \
                       devid + '.route')

        # bug #78043
        # we should have device specific gateways
        # fixed this way, until we have a way to mark the
        # default GATEWAY/GATEWAYDEV
        cfg = Conf.ConfShellVar(getRoot() + SYSCONFNETWORK)
        if cfg.has_key('GATEWAY'):
            del cfg['GATEWAY']
        if cfg.has_key('GATEWAYDEV'):
            del cfg['GATEWAYDEV']
        cfg.write()

        self.commit(False) # pylint: disable-msg=E1101
        self.setChanged(False) # pylint: disable-msg=E1101

__DVList = None
__DVList_root = getRoot()

def getDeviceList(refresh = None):
    global __DVList
    global __DVList_root
    if __DVList == None or refresh or \
           __DVList_root != getRoot():
        __DVList = DeviceList()
        __DVList.load()
        __DVList_root = getRoot()
    return __DVList

def getNextDev(base):
    devlist = getDeviceList()
    num = 0
    for num in xrange(0,100):
        for dev in devlist:
            if dev.Device == base + str(num):
                break
        else:
            # no card seems to use this
            break

    return base + str(num) # pylint: disable-msg=W0631

__author__ = "Harald Hoyer <harald@redhat.com>"