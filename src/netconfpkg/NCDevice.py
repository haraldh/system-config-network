## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Than Ngo <than@redhat.com>
## Copyright (C) 2001 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001 Philipp Knirsch <pknirsch@redhat.com>

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
import string
import commands
import math
import NC_functions

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

import Conf
import gettext

import HardwareList

from NC_functions import *
import DeviceList
import NCDialup
import NCCipe

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class ConfDevice(Conf.ConfShellVar):
    def __init__(self, name):
        Conf.ConfShellVar.__init__(self, SYSCONFDEVICEDIR + 'ifcfg-' + name)
        self.chmod(0600)

class ConfRoute(Conf.ConfShellVar):
    def __init__(self, name):
        Conf.ConfShellVar.__init__(self, SYSCONFDEVICEDIR + name + '.route')
        self.chmod(0600)

class Device(DeviceList.Device_base):
    keydict = { 'Device' : 'DEVICE',
                'Name' : 'NAME',
                'OnBoot' : 'ONBOOT',
                'IP' : 'IPADDR',
                'Netmask' : 'NETMASK',
                'Gateway' : 'GATEWAY',
                'Hostname' : 'DEVHOSTNAME',
                'Domain' : 'DOMAIN',
                'BootProto' : 'BOOTPROTO',
                'Type' : 'TYPE',
                'HardwareAddress' : 'HWADDR',
                }

    boolkeydict = { 'OnBoot' : 'ONBOOT',
                    'AllowUser' : 'USERCTL',
                    'AutoDNS' : 'PEERDNS',
                    }
        
    def __init__(self, list = None, parent = None):
        DeviceList.Device_base.__init__(self, list, parent)        

    def apply(self, other):
        if not other:
            self.unlink()
            return
        # ApplyList
        self.setDeviceId(other.getDeviceId())
        self.setName(other.getName())
        self.setDevice(other.getDevice())
        self.setAlias(other.getAlias())
        self.setType(other.getType())
        self.setOnBoot(other.getOnBoot())
        self.setAllowUser(other.getAllowUser())
        self.setBootProto(other.getBootProto())
        self.setIP(other.getIP())
        self.setNetmask(other.getNetmask())
        self.setGateway(other.getGateway())
        self.setHostname(other.getHostname())
        self.setDomain(other.getDomain())
        self.setAutoDNS(other.getAutoDNS())
        self.setHardwareAddress(other.getHardwareAddress())
        self.createStaticRoutes().apply(other.getStaticRoutes())
        self.createCipe().apply(other.getCipe())
        self.createWireless().apply(other.getWireless())
        if self.createDialup():
            self.Dialup.apply(other.getDialup())

    def createDialup(self):
        if self.Type:
            if self.Type == "Modem":
                if (self.Dialup == None) \
                   or not isinstance(self.Dialup, NCDialup.ModemDialup):
                    self.Dialup = NCDialup.ModemDialup(None, self)
            elif self.Type == "ISDN":
                if (self.Dialup == None) \
                   or not isinstance(self.Dialup, NCDialup.IsdnDialup):
                    self.Dialup = NCDialup.IsdnDialup(None, self)
            elif self.Type == "xDSL":
                if (self.Dialup == None) \
                   or not isinstance(self.Dialup, NCDialup.DslDialup):
                    self.Dialup = NCDialup.DslDialup(None, self)
            else:
                self.Dialup = None
                
            return self.Dialup

        else:
            raise TypeError, _("Device type not specified")

    def createCipe(self):
        if self.Type:
            if self.Type == "CIPE":
                DeviceList.Device_base.createCipe(self)
            else: self.Cipe = None
                
            return self.Cipe

        else:
            raise TypeError, _("Device type not specified")

    def createWireless(self):
        if self.Type:
            if self.Type == "Wireless":
                DeviceList.Device_base.createWireless(self)
            else: self.Wireless = None
                
            return self.Wireless

        else:
            raise TypeError, _("Device type not specified")


    def load(self, name):
        
        conf = ConfDevice(name)
        rconf = ConfRoute(name)

        self.DeviceId = name
        
        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                self.__dict__[selfkey] = conf[confkey]

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'yes':
                    self.__dict__[selfkey] = true
                else:
                    self.__dict__[selfkey] = false            
            else:
                self.__dict__[selfkey] = false            

        if not self.Gateway:
            try:
                cfg = Conf.ConfShellVar(SYSCONFNETWORK)
                if cfg.has_key('GATEWAY'):
                    gw = cfg['GATEWAY']
                    
                    if gw and self.Netmask:                    
                        network = commands.getoutput('ipcalc --network ' + str(self.IP) \
                                            + ' ' + str(self.Netmask) + \
                                            ' 2>/dev/null')
                        
                        out = commands.getoutput('ipcalc --network ' + str(gw) + ' ' \
                                        + str(self.Netmask) + ' 2>/dev/null')
                        
                        if out == network:
                            self.Gateway = str(gw)
                            
            except (OSError, IOError), msg:
                pass

        aliaspos = string.find(self.Device, ':')
        if aliaspos != -1:
            self.Alias = int(self.Device[aliaspos+1:])
            self.Device = self.Device[:aliaspos]

        if not self.Type or self.Type == "" or self.Type == "Unknown":
            hwlist = HardwareList.getHardwareList()
            for hw in hwlist:
                if hw.Name == self.Device:
                    self.Type = hw.Type
                    break
                    
        if (not self.Type or self.Type == "" or self.Type == "Unknown" ) \
           and self.Device:            
            self.Type = NC_functions.getDeviceType(self.Device)

        #print "Creating Dialup"
        dialup = self.createDialup()
        if dialup:
            #print "Loading Dialup"
            dialup.load(conf)

        cipe = self.createCipe()
        if cipe:
            cipe.load(conf)

        wireless = self.createWireless()
        if wireless:
            wireless.load(conf)

        num = len(rconf.keys())
        self.createStaticRoutes()

        if math.fmod(num, 3) != 0:
            print _("Static routes file for ") + name \
                  + _(" has not vaild format")
        else:
            for p in xrange(0, num/3):
                i = self.StaticRoutes.addRoute()
                route = self.StaticRoutes[i]
                route.Address = rconf['ADDRESS'+str(p)]
                route.Netmask = rconf['NETMASK'+str(p)]
                route.Gateway = rconf['GATEWAY'+str(p)]
        self.commit()
                
    def save(self):
        self.commit()

        conf = ConfDevice(self.DeviceId)

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        if self.Alias != None:
            conf['DEVICE'] = str(self.Device) + ':' + str(self.Alias)

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = 'yes'
            else:
                conf[confkey] = 'no'
                    
        if self.Dialup:
            self.Dialup.save(conf)

        if self.Cipe:
            self.Cipe.save(conf)

        if self.Wireless:
            self.Wireless.save(conf)

        if self.StaticRoutes and len(self.StaticRoutes) > 0:
            rconf = ConfRoute(self.DeviceId)
            p = 0
            for route in self.StaticRoutes:
                rconf['ADDRESS'+str(p)] = route.Address
                rconf['NETMASK'+str(p)] = route.Netmask
                rconf['GATEWAY'+str(p)] = route.Gateway
                p = p + 1
            rconf.write()

        for i in conf.keys():
            if not conf[i] or conf[i] == "": del conf[i]

        conf.write()
