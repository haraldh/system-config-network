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

_hwFac = None

def getHardwareFactory():
    global _hwFac
    
    if _hwFac == None:
        _hwFac = HardwareFactory()

    return _hwFac

from NC_functions import log
from netconfpkg.NCHardware import Hardware
import NCDevice

class HardwareFactory(dict):
    def register(self, theclass, hwtype, subtype = None):
        if not issubclass(theclass, Hardware):
            raise ValueError, "First argument has to be a subclass of Hardware!"        
        if not subtype:
            if self.has_key(hwtype):
                #raise KeyError, "%s is already registered" % hwtype
                log.log(1, "KeyError, %s is already registered" % hwtype)
                return
            else:
                self[hwtype] = { 0 : theclass }
        else:
            if self.has_key(hwtype) and self[hwtype].has_key(subtype):
                #raise KeyError, "%s.%s is already registered" % (hwtype, subtype)
                log.log(1, "KeyError %s.%s is already registered" % (hwtype, subtype))
                return
            else:
                if not self.has_key(hwtype):
                    self[hwtype] = {}
                self[hwtype][subtype] = theclass

    def getHardwareClass(self, hwtype, subtype = None):        
        if not self.has_key(hwtype):
            log.log(1, "Error: %s not in HardwareFactory!" % hwtype)
            return Hardware
        if subtype and self[type].has_key(subtype):
            return self[hwtype][subtype]
        else:
            return self[hwtype][0]
            

from netconfpkg.plugins import *
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2004/06/29 14:13:51 $"
__version__ = "$Revision: 1.9 $"
