## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>

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

            
_devFac = None

from rhpl.log import log

def getDeviceFactory():
    global _devFac
    
    if _devFac == None:
        _devFac = DeviceFactory()

    return _devFac

#from NC_functions import *
from netconfpkg.NCDevice import Device

class DeviceFactory(dict):
    def register(self, theclass, devtype, subtype = None):
        if not issubclass(theclass, Device):
            raise ValueError, "first argument has to be a subclass of Device"
            
        if not subtype:
            if self.has_key(devtype):
                #raise KeyError, "%s is already registered" % devtype
                log.log(1, "KeyError, %s is already registered" % devtype)
                return
            else:
                self[devtype] = { 0 : theclass }
        else:
            if self.has_key(devtype) and self[devtype].has_key(subtype):
                #raise KeyError, "%s.%s is already registered" % (devtype, subtype)
                log.log(1, "KeyError, %s.%s is already registered" % (devtype, subtype))
                return
            else:
                if not self.has_key(devtype):
                    self[devtype] = {}
                self[devtype][subtype] = theclass

    def getDeviceClass(self, devtype, subtype = None):
        if not self.has_key(devtype):
            log.log(1, "Error: %s not in DeviceFactory!" % devtype)
            return Device
        
        if subtype and self[devtype].has_key(subtype):
            return self[devtype][subtype]
        else:
            return self[devtype][0]

from netconfpkg.plugins import *
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/07/08 09:45:48 $"
__version__ = "$Revision: 1.8 $"
