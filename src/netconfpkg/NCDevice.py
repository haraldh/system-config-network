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
import string
import commands
import math
import NC_functions

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
from rhpl import Conf
from rhpl import ConfSMB
from NC_functions import *
from netconfpkg import Device_base
import NCDialup
import NCCipe
from rhpl.log import log
from rhpl.executil import gtkExecWithCaptureStatus

class ConfDevice(Conf.ConfShellVar):
    def __init__(self, name):
        new = false
        self.filename = netconfpkg.ROOT + SYSCONFDEVICEDIR + 'ifcfg-' + name
        if not os.access(self.filename, os.R_OK):
            new = true
            self.oldmode = 0644
        else:
            status = os.stat(self.filename)
            self.oldmode = status[0]
            #print status
            
        Conf.ConfShellVar.__init__(self, self.filename)
        
        if new:
            self.rewind()
            self.insertline("# Please read /usr/share/doc/"
                            "initscripts-*/sysconfig.txt")
            self.nextline()
            self.insertline("# for the documentation of these parameters.");
            self.rewind()
    
    def write(self):
        self.chmod(self.oldmode)
        log.log(2, "chmod %#o %s" % (self.oldmode & 03777, self.filename))
        #if ((self.oldmode & 0044) != 0044):
        #    ask = NC_functions.generic_yesno_dialog(\
        #        _("May I change\n%s\nfrom mode %o to %o?") % \
        #        (self.filename, self.oldmode & 03777, 0644))
        #    if ask != RESPONSE_YES:
        #        self.chmod(self.oldmode)
        Conf.ConfShellVar.write(self)
            
class ConfRoute(Conf.ConfShellVar):
    def __init__(self, name):
        Conf.ConfShellVar.__init__(self, netconfpkg.ROOT + SYSCONFDEVICEDIR + 'route-' + name)
        self.chmod(0644)

class Device(Device_base):
    keydict = { 'Device' : 'DEVICE',
                'IP' : 'IPADDR',
                'Netmask' : 'NETMASK',
                'Gateway' : 'GATEWAY',
                'Hostname' : 'DHCP_HOSTNAME',
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
        Device_base.__init__(self, list, parent)        
        self.oldname = None

#     def __str__(self):
#         if self.Alias != None:
#             return "Device %s (%s:%d)" % (self.DeviceId, self.Device,
#                                           self.Alias)
#         else:
#             return "Device %s (%s)" % (self.DeviceId, self.Device)

#     def __repr__(self):
#         if self.Alias != None:
#             return "Device %s (%s:%d)" % (self.DeviceId, self.Device,
#                                       self.Alias)
#         else:
#             return "Device %s (%s)" % (self.DeviceId, self.Device)


    def getDialog(self):
        raise NotImplemented

    def getWizard(self):
        raise NotImplemented

    def isType(self, device):
        raise NotImplemented

    def testDeviceId(self, value, child = None):
        if re.search(r"^[a-z|A-Z|0-9\_:]+$", value):
            return true
        return false

    def getDeviceAlias(self):
        devname = self.Device
        if self.Alias and self.Alias != "":
            devname = devname + ':' + str(self.Alias)
        return devname

    def load(self, name):
        from netconfpkg.NCDeviceList import getDeviceList
        conf = ConfDevice(name)

        self.oldname = name

        if not conf.has_key("DEVICE"):
            aliaspos = string.find(name, ':')
            if aliaspos != -1:
                # ok, we have to inherit all other data from our master
                for dev in getDeviceList():
                    if dev.Device == name[:aliaspos]:
                        self.apply(dev)
                        break

            self.Device = name
         
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
            elif not self.__dict__.has_key(selfkey):
                self.__dict__[selfkey] = false                            
            
        if not self.Gateway:
            try:
                cfg = Conf.ConfShellVar(netconfpkg.ROOT + SYSCONFNETWORK)
                if cfg.has_key('GATEWAY'):
                    gw = cfg['GATEWAY']
                    
                    if gw and self.Netmask:
                        try:
                            network = commands.getoutput('ipcalc --network '+\
                                                         str(self.IP) + \
                                                         ' ' + \
                                                         str(self.Netmask) +\
                                                         ' 2>/dev/null')
                            
                            out = commands.getoutput('ipcalc --network ' + \
                                                     str(gw) + ' ' \
                                                     + str(self.Netmask) + \
                                                     ' 2>/dev/null')
                            if out == network:
                                self.Gateway = str(gw)
                        except:
                            pass
                        
                            
            except EnvironmentError, msg:
                NC_functions.generic_error_dialog(str(msg))
                pass

        try:
            aliaspos = string.find(self.Device, ':')
            if aliaspos != -1:
                self.Alias = int(self.Device[aliaspos+1:])
                self.Device = self.Device[:aliaspos]
        except TypeError:
            NC_functions.generic_error_dialog(_("%s, "
                                                "Device not specified "
                                                "or alias not a number!") % \
                                              self.DeviceId)
            #raise TypeError, _("Device not specified or alias not a number!")

        if not self.Type or self.Type == "" or self.Type == _("Unknown"):
            import NCHardwareList
            hwlist = NCHardwareList.getHardwareList()
            for hw in hwlist:
                if hw.Name == self.Device:
                    self.Type = hw.Type
                    break
            else:
                self.Type = NC_functions.getDeviceType(self.Device)

        if conf.has_key("RESOLV_MODS"):
            if conf["RESOLV_MODS"] != "no":
                self.AutoDNS = true
            else:
                self.AutoDNS = false

        if self.Type == CTC or self.Type == IUCV:
            if conf['MTU']:
                self.Mtu = conf['MTU']

        # move old <id>.route files to route-<id>
        file = netconfpkg.ROOT + SYSCONFDEVICEDIR + \
                                self.DeviceId + '.route'
        if os.path.isfile(file):
            NC_functions.rename(file,
                                netconfpkg.ROOT + SYSCONFDEVICEDIR + \
                                'route-' + self.DeviceId )
        # load routes
        rconf = ConfRoute(name)
        num = len(rconf.keys())
        self.createStaticRoutes()

        # XXX fixme
        if math.fmod(num, 3) != 0:
             NC_functions.generic_error_dialog((_("Static routes file %s "
                                                  "is invalid")) % name)
        else:
            for p in xrange(0, int(num/3)):
                i = self.StaticRoutes.addRoute()
                route = self.StaticRoutes[i]
                route.Address = rconf['ADDRESS' + str(p)]
                route.Netmask = rconf['NETMASK' + str(p)]
                route.Gateway = rconf['GATEWAY' + str(p)]
        
        self.commit(changed=false)
                
    def save(self):
        # Just to be safe...
        os.umask(0022)
        self.commit()

        if self.oldname and (self.oldname != self.DeviceId):
            for prefix in [ 'ifcfg-', 'route-', 'keys-' ]:
                NC_functions.rename(netconfpkg.ROOT + SYSCONFDEVICEDIR + \
                                    prefix + self.oldname,
                                    netconfpkg.ROOT + SYSCONFDEVICEDIR + \
                                    prefix + self.DeviceId)            

        conf = ConfDevice(self.DeviceId)
        conf.fsf()
        
        if not self.Cipe and self.BootProto == None \
           and (self.IP == None or self.IP == ""):
            self.BootProto = 'dhcp'
                
        if self.BootProto:
            self.BootProto = string.lower(self.BootProto)

        if self.BootProto == "static":
            self.BootProto = "none"

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

        # Recalculate BROADCAST and NETWORK values if IP and netmask are
        # present (#51462)
        # obsolete
        if self.IP and self.Netmask and conf.has_key('BROADCAST'):
            try:
                broadcast = commands.getoutput('ipcalc --broadcast ' + \
                                               str(self.IP) + \
                                               ' ' + str(self.Netmask) + \
                                               ' 2>/dev/null')
                if broadcast:
                    conf['BROADCAST'] = broadcast[10:]
            except:
                pass

        if self.IP and self.Netmask and conf.has_key('NETWORK'):
            try:
                network = commands.getoutput('ipcalc --network ' + \
                                             str(self.IP) + \
                                             ' ' + str(self.Netmask) + \
                                             ' 2>/dev/null')
                if network:
                    conf['NETWORK'] = network[8:]
            except:
                pass                
        else:
            del conf['NETWORK']
            del conf['BROADCAST']

        if self.Type == CTC or self.Type == IUCV:
            if not self.Mtu: self.Mtu = 1492
            conf['MTU'] = self.Mtu
            if conf['GATEWAY']:
                conf['REMIP'] = conf['GATEWAY']

        if self.Dialup:
            self.Dialup.save(conf)

        if self.Cipe:
            self.Cipe.save(conf)

        if self.Wireless:
            self.Wireless.save(conf)

        if self.StaticRoutes and len(self.StaticRoutes) > 0:
            rconf = ConfRoute(self.DeviceId)
            for key in rconf.keys():
                del rconf[key]
            p = 0
            for route in self.StaticRoutes:
                if route.Address:
                    rconf['ADDRESS'+str(p)] = route.Address
                if route.Netmask:
                    rconf['NETMASK'+str(p)] = route.Netmask
                if route.Gateway:
                    rconf['GATEWAY'+str(p)] = route.Gateway
                p = p + 1
            rconf.write()
            
        # Do not clear the non-filled in values for Wireless Devices
        # Bugzilla #52252
        if not self.Wireless:
            for i in conf.keys():
                if not conf[i] or conf[i] == "":
                    del conf[i]

        # RESOLV_MODS should be PEERDNS
        if conf.has_key('RESOLV_MODS'):
            del conf['RESOLV_MODS']

        conf.write()

        self.oldname = self.DeviceId
        
    def activate(self, dialog = None):        
        if self.Type == ISDN:
            command = '/usr/sbin/isdnup'
            param = [command, self.getDeviceAlias()]
        else:
            command = '/sbin/ifup'
            param = [command, self.DeviceId, "up"]

        try:
            (ret, msg) =  generic_run_dialog(\
                command,
                param,
                catchfd = (1,2),
                title = _('Network device activating...'),
                label = _('Activating network device %s, '
                          'please wait...') % (self.DeviceId),
                errlabel = _('Cannot activate '
                             'network device %s!\n') % (self.DeviceId),
                dialog = dialog)
            
        except RuntimeError, msg:
            ret = -1        

        return ret, msg

    def deactivate(self, dialog = None):
        command = '/sbin/ifdown'
        param = [command, self.DeviceId, "down"]
        
        try:
            (ret, msg) = generic_run_dialog(\
                command, param,
                catchfd = (1,2),
                title = _('Network device deactivating...'),
                label = _('Deactivating network device %s, '
                          'please wait...') % (self.DeviceId),
                errlabel = _('Cannot deactivate '
                             'network device %s!\n') % (self.DeviceId),
                dialog = dialog)
            
        except RuntimeError, msg:
            ret = -1

        return ret, msg

    def configure(self):
        command = '/usr/bin/redhat-config-network'

        try:
            (ret, msg) =  generic_run(command,
                                      [command],
                                      catchfd = (1,2))
        except RuntimeError, msg:
            ret = -1
            
        return ret, msg

    def monitor(self):
        pass

    def getHWDevice(self):
        return self.Device

##     def _createAttr(self, child=None):
##         if not hasattr(self, "Dialup") or not self.Dialup:
##             log.log(4, "createAttr(%s)" % child)
##             # not exactly OO...
##             from netconfpkg.NCDeviceFactory import getDeviceFactory
##             df = getDeviceFactory()
##             devclass = None
##             if self.Type:
##                 devclass = df.getDeviceClass(self.Type)
##             else:
##                 log.log(4, "createAttr(%s) - Type not set" % child)
##             if devclass:
##                 newdev = devclass()
##                 if hasattr(newdev, "create" + child):
##                     func = getattr(newdev, "create" + child)
##                     setattr(self, child, func())
##             else:
##                 log.log(4, "createAttr(%s) - no devclass" % child)
##                 return Device_base._createAttr(self, child)
##         return getattr(self, child)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/07/30 12:37:20 $"
__version__ = "$Revision: 1.90 $"
