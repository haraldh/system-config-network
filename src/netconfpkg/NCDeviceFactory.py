## Copyright (C) 2001, 2002 Red Hat, Inc.
## Copyright (C) 2001, 2002 Harald Hoyer <harald@redhat.com>

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

from NC_functions import *
from netconfpkg.NCDevice import Device

class DeviceFactory(dict):
    def register(self, theclass, type, subtype = None):
        if not issubclass(theclass, Device):
            raise ValueError, "first argument has to be a subclass of Device"
            
        if not subtype:
            if self.has_key(type):
                raise KeyError, "%s is already registered" % type
            else:
                self[type] = { 0 : theclass }
        else:
            if self.has_key(type) and self[type].has_key(subtype):
                raise KeyError, "%s.%s is already registered" % (type, subtype)
            else:
                if not self.has_key(type):
                    self[type] = {}
                self[type][subtype] = theclass

    def getDeviceClass(self, type, subtype = None):
        if subtype and self[type].has_key(subtype):
            return self[type][subtype]
        else:
            return self[type][0]
            
_devFac = None

def getDeviceFactory():
    global _devFac
    
    if _devFac == None:
        _devFac = DeviceFactory()

    return _devFac