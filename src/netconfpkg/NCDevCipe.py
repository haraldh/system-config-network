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

from netconfpkg.NCDevice import Device
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import *

_devCipeDialog = None
_devCipeWizard = None

class DevCipe(Device):    
   def __init__(self, list = None, parent = None):
       Device.__init__(self, list, parent)

   def getDialog(self):
       return _devCipeDialog(self).xml.get_widget("Dialog")
    
   def getWizard(self):
       return _devCipeWizard

   def isType(self, device):
       if device.Type == ETHERNET:
           return true
       if getDeviceType(device.Device) == ETHERNET:
           return true
       return false

def setDevCipeDialog(dialog):
    global _devCipeDialog
    _devCipeDialog = dialog

def setDevCipeWizard(wizard):
    global _devCipeWizard
    _devCipeWizard = wizard

df = getDeviceFactory()
df.register(DevCipe, ETHERNET)
