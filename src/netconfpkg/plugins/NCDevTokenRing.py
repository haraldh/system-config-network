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

from netconfpkg.NCDevice import Device
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import *

_devTokenRingDialog = None
_devTokenRingWizard = None

class DevTokenRing(Device):    
   def __init__(self, list = None, parent = None):
       Device.__init__(self, list, parent)
       self.Type = TOKENRING

   def getDialog(self):
       return _devTokenRingDialog(self).xml.get_widget("Dialog")
    
   def getWizard(self):
       return _devTokenRingWizard

   def isType(self, device):
       if device.Type == TOKENRING:
           return true
       if getDeviceType(device.Device) == TOKENRING:
           return true
       return false

def setDevTokenRingDialog(dialog):
    global _devTokenRingDialog
    _devTokenRingDialog = dialog

def setDevTokenRingWizard(wizard):
    global _devTokenRingWizard
    _devTokenRingWizard = wizard

df = getDeviceFactory()
df.register(DevTokenRing, TOKENRING)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/07/08 09:45:48 $"
__version__ = "$Revision: 1.4 $"
