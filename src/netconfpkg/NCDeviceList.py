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

import os
import os.path
import string

from NC_functions import *
#from netconfpkg.NCDevice import Device
from netconfpkg import DeviceList_base
from netconfpkg.NCDeviceFactory import getDeviceFactory
from rhpl import ConfSMB
from rhpl import Conf
from rhpl.log import log

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")


def updateNetworkScripts():
    if os.getuid() == 0:
        if not os.path.isdir(netconfpkg.ROOT + SYSCONFDEVICEDIR):
            mkdir(netconfpkg.ROOT + SYSCONFDEVICEDIR)

        if not os.path.isdir(netconfpkg.ROOT + SYSCONFPROFILEDIR):
            mkdir(netconfpkg.ROOT + SYSCONFPROFILEDIR)

        if not os.path.isdir(netconfpkg.ROOT + SYSCONFPROFILEDIR+'/default/'):
            mkdir(netconfpkg.ROOT + SYSCONFPROFILEDIR+'/default/')

    devlist = os.listdir(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR)
    changed = false
    for dev in devlist:
        if dev[:6] != 'ifcfg-' or dev == 'ifcfg-lo' or string.find(dev, '.rpmsave') != -1 or string.find(dev, '.rpmnew') != -1:
            continue

        if os.path.islink(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+'/'+dev) or ishardlink(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+'/'+dev):
            log.log(4, dev+" already a link, skipping it.")
            continue

        if getDeviceType(dev[6:]) == _('Unknown'):
            log.log(4, dev+" has unknown device type, skipping it.")
            continue


        if os.getuid() != 0:
            generic_error_dialog (_("Please start redhat-config-network "
                                    "with root permissions once!\n"))
            return

        log.log(1, _("Copying %s to devices and putting "
                     "it into the default profile.") % dev)

        unlink(netconfpkg.ROOT + SYSCONFPROFILEDIR+'/default/'+dev)

        copy(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+'/'+dev, netconfpkg.ROOT + SYSCONFDEVICEDIR+'/'+dev)
        link(netconfpkg.ROOT + SYSCONFDEVICEDIR+'/'+dev, netconfpkg.ROOT + SYSCONFPROFILEDIR+'/default/'+dev)    
        changed = true
    return changed

class DeviceList(DeviceList_base):
    def __init__(self, list = None, parent = None):
        DeviceList_base.__init__(self, list, parent)        


    def load(self):
        from NCDevice import ConfDevice
        changed = updateNetworkScripts()

        self.__delslice__(0, len(self))

        df = getDeviceFactory()
        devices = ConfDevices()
        msg = ""
        for dev in devices:
            conf = ConfDevice(dev)
            type = None
            device = None
            # take a peek in the config file
            if conf.has_key("TYPE"):
                type = conf["TYPE"]
            if conf.has_key("DEVICE"):
                device = conf["DEVICE"]
            del conf

            if type == "IPSEC":
                continue

            if not type or type == "" or type == _("Unknown"):
                import NCHardwareList
                hwlist = NCHardwareList.getHardwareList()
                for hw in hwlist:
                    if hw.Name == device:
                        type = hw.Type
                        break
                else:
                    type = getDeviceType(device)
                    
            devclass = df.getDeviceClass(type)
            if devclass:
                newdev = devclass()
                newdev.load(dev)
                self.append(newdev)
            else:
                log.log(1, "NO DEVICE CLASS FOUND FOR %s" % dev)
                i = self.addDevice()
                self[i].load(dev)
                
        self.commit(changed)

        chdev = {}
        # the initscripts do not like '-'
        for dev in self:
            newDeviceId = re.sub('-', '_', dev.DeviceId)
            if newDeviceId != dev.DeviceId:
                chdev[dev.DeviceId] = newDeviceId
                #log.log(4, "%s != %s" % (newDeviceId, dev.DeviceId))
                # Fixed change device names in active list of all profiles
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
                dev.commit()

        if len(chdev.keys()):
            s =_("Changed the following Nicknames due to the initscripts:\n")
            for n, d in chdev.items():
                s += "%s -> %s\n" % (n, d)
            generic_longinfo_dialog(_("Nicknames changed"), s)


    def addDeviceType(self, type):
        df = getDeviceFactory()
        devclass = df.getDeviceClass(type)
        i = self.addDevice()
        if devclass:
            newdev = devclass()
            self[i] = newdev
        return self[i]
    
    def test(self):
        pass

    def __repr__(self):
        return repr(self.__dict__)

    def _objToStr(self, parentStr = None):
        #return DeviceList_base._objToStr(self, obj, parentStr)
        retstr = ""
        for dev in self:
            retstr += dev._objToStr("DeviceList.%s.%s" % (dev.Type,
                                                          dev.DeviceId))

        return retstr


    def _parseLine(self, vals, value):
        class BadLineException: pass
        if len(vals) <= 1:
            return
        if vals[0] == "DeviceList":
            del vals[0]
        else:
            return
        for dev in self:
            if dev.DeviceId == vals[1]:
                if dev.Type != vals[0]:
                    self.pop(dev)
                    log.log(1, "Deleting device %s" % vals[1] )
                    break
                dev._parseLine(vals[2:], value)
                return
        
        dev = self.addDeviceType(vals[0])
        dev.DeviceId = vals[1]
        dev._parseLine(vals[2:], value)
    
    def save(self):
        from NCDevice import ConfDevice
        from types import DictType
        self.commit(changed=false)

        nwconf = Conf.ConfShellVar(netconfpkg.ROOT + SYSCONFNETWORK)
        if len(self) > 0:
            nwconf["NETWORKING"] = "yes"
        nwconf.write()

        #
        # clear all Dialer sections in wvdial.conf
        # before the new Dialer sections written
        #
        wvdialconf = ConfSMB.ConfSMB(filename = netconfpkg.ROOT + WVDIALCONF)
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

        #
        # Remove old config files
        #
        try:
            dir = os.listdir(netconfpkg.ROOT + SYSCONFDEVICEDIR)
        except OSError, msg:
            raise IOError, 'Cannot save in ' \
                  + netconfpkg.ROOT + SYSCONFDEVICEDIR + ': ' + str(msg)

        for entry in dir:
            if (len(entry) <= 6) or \
               entry[:6] != 'ifcfg-' or \
               (not os.path.isfile(netconfpkg.ROOT + SYSCONFDEVICEDIR + entry)):
                continue
            
            devid = entry[6:]
            for dev in self:
                if dev.DeviceId == devid:
                    break
            else:
                # check for IPSEC
                conf = ConfDevice(entry)
                type = None
                if conf.has_key("TYPE"): type = conf("TYPE")
                if type == IPSEC:
                    continue

                # now remove the file
                unlink(netconfpkg.ROOT + SYSCONFDEVICEDIR + entry)
                log.log(2, "rm %s" % (netconfpkg.ROOT + SYSCONFDEVICEDIR + entry))
                unlink(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+'/ifcfg-'+devid)
                log.log(2, "rm %s" % (netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+'/ifcfg-'+devid))

        # remove old route files
        for entry in dir:
            if (len(entry) <= 6) or \
               entry[:6] != '.route' or \
               (not os.path.isfile(netconfpkg.ROOT + SYSCONFDEVICEDIR + entry)):
                continue
            devid = entry[6:]
                
            for dev in self:
                if dev.DeviceId == devid:
                    break
            else:
                # remove route file, if no routes defined
                unlink(netconfpkg.ROOT + SYSCONFDEVICEDIR + entry)
                log.log(2, "rm %s" % (netconfpkg.ROOT + SYSCONFDEVICEDIR + entry))
                unlink(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+devid+'.route')
                log.log(2, "rm %s" % (netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+devid+'.route'))


        # bug #78043
        # we should have device specific gateways
        # fixed this way, until we have a way to mark the
        # default GATEWAY/GATEWAYDEV
        cfg = Conf.ConfShellVar(netconfpkg.ROOT + SYSCONFNETWORK)
        if cfg.has_key('GATEWAY'):
            del cfg['GATEWAY']
        if cfg.has_key('GATEWAYDEV'):
            del cfg['GATEWAYDEV']
        cfg.write()
        
        self.commit()

DVList = None

def getDeviceList(refresh = None):
    global DVList
    if DVList == None or refresh:
        DVList = DeviceList()
        DVList.load()
    return DVList

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
        
    return base + str(num)

                
if __name__ == '__main__':
    dl = DeviceList()
    dl.load()
    for dev in dl:
        if dev.Type == "Ethernet":
            continue
            print "ID: " + str(dev.DeviceId)
            print "Name: " + str(dev.Name)
            print "Device: " + str(dev.Device)
            print "Alias: " + str(dev.Alias)
            print "Type: " + str(dev.Type)
            print "OnBoot: " + str(dev.OnBoot)
            print "AllowUser: " + str(dev.AllowUser)
            print "BootProto: " + str(dev.BootProto)
            print "IP: " + str(dev.IP)
            print "Netmask: " + str(dev.Netmask)
            print "Gateway: " + str(dev.Netmask)
            print "Hostname: " + str(dev.Hostname)
            print "Domain: " + str(dev.Domain)
            print "AutoDNS: " + str(dev.AutoDNS)
        elif dev.Type == "Modem" or dev.Type == "ISDN":
            print "Device: ", str(dev.Device)
            print "Provider Name: " + str(dev.Dialup.ProviderName)
            print "Login: " + str(dev.Dialup.Login)
            print "Password: " + str(dev.Dialup.Password)
            print "Authentication: " + str(dev.Dialup.Authentication)
            print "MSN: " + str(dev.Dialup.MSN)
            print "Prefix: " + str(dev.Dialup.Prefix)
            print "Areacode: " + str(dev.Dialup.Areacode)
            print "Regioncode: " + str(dev.Dialup.Regioncode)
            print "PhoneNumber: " + str(dev.Dialup.PhoneNumber)
            print "LocalIP: " + str(dev.Dialup.LocalIP)
            print "RemoteIP: " + str(dev.Dialup.RemoteIP)
            print "PrimaryDNS: " + str(dev.Dialup.PrimaryDNS)
            print "SecondaryDNS: " + str(dev.Dialup.SecondaryDNS)
            print "Persist: " + str(dev.Dialup.Persist)
            print "DefRoute: " + str(dev.Dialup.DefRoute)
            print "ChargeHup: " + str(dev.Dialup.ChargeHup)
            print "ChargeInt: " + str(dev.Dialup.ChargeInt)
            print "Ihup: " + str(dev.Dialup.Ihup)
            print "DialMax: " + str(dev.Dialup.DialMax)
            print "Layer2: " + str(dev.Dialup.Layer2)
            print "PPP Options: " , dev.Dialup.PPPOptions
            if dev.Dialup.DialinServer:
                print "DialinServer: yes"
            else:
                print "DialinServer: no"
            if dev.Dialup.ChannelBundling:
                print "ChannelBundling: yes"
            else:
                print "ChannelBundling: no"
            print "EncapMode: " + str(dev.Dialup.EncapMode)
            print "HangupTimeout: " + str(dev.Dialup.HangupTimeout)
            print "DialMode: " + str(dev.Dialup.DialMode)
            print "SlaveDevice: " + str(dev.Dialup.SlaveDevice)
            if dev.Dialup.Secure:
                print "Secure: yes"
            else:
                print "Secure: no"
            print "InitStrings: ", dev.Dialup.InitStrings
            print "Callback:", dev.Dialup.Callback
            #if dev.Dialup.Callback == None:
            print "  Number:",  dev.Dialup.Callback.Number
            print "  Delay:", dev.Dialup.Callback.Hup
            if dev.Dialup.Callback.CBCP:
                print "  CBCP: yes"
            else:
                print "  CBCP: no"
            
            print "Compression:"
            if dev.Dialup.Compression:
                if dev.Dialup.Compression.VJTcpIp:
                    print "  VJTcpIp: yes"
                else:
                    print "  VJTcpIp: no"
                if dev.Dialup.Compression.VJID:
                    print "  VJID: yes"
                else:
                    print "  VJID: no"
                if dev.Dialup.Compression.AdressControl:
                    print "  AdressControl: yes"
                else:
                    print "  AdressControl: no"
                if dev.Dialup.Compression.ProtoField:
                    print "  ProtoField: yes"
                else:
                    print "  ProtoField: no"
                if dev.Dialup.Compression.BSD:
                    print "  BSD: yes"
                else:
                    print "  BSD: no"
                if dev.Dialup.Compression.CCP:
                    print "  CCP: yes"
                else:
                    print "  CCP: no"
                                        
            
        print "---------------------------------------"
    #dl.save()
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/07/08 09:45:48 $"
__version__ = "$Revision: 1.57 $"
