## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>

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

from netconfpkg.NCDevice import *
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import *

_devWirelessDialog = None
_devWirelessWizard = None

class DevWireless(Device):    
   def __init__(self, list = None, parent = None):
      Device.__init__(self, list, parent)
      self.Type = WIRELESS
      self.createWireless()
      
   def load(self, name):
      conf = ConfDevice(name)
      Device.load(self, name)
      self.Wireless.load(conf)

   def createWireless(self):
      Device.createWireless(self)
      return self.Wireless
   
   def getDialog(self):
      return _devWirelessDialog(self).xml.get_widget("Dialog")
    
   def getWizard(self):
      return _devWirelessWizard

   def isType(self, device):
      if device.Type == WIRELESS:
         return true
      if getDeviceType(device.Device) == WIRELESS:
         return true
      return false

def setDevWirelessDialog(dialog):
   global _devWirelessDialog
   _devWirelessDialog = dialog

def setDevWirelessWizard(wizard):
   global _devWirelessWizard
   _devWirelessWizard = wizard

df = getDeviceFactory()
df.register(DevWireless, WIRELESS)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2005/03/03 17:25:26 $"
__version__ = "$Revision: 1.7 $"
