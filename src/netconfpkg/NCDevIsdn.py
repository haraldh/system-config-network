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

from netconfpkg import NCDialup

_devIsdnDialog = None
_devIsdnWizard = None

class DevIsdn(Device):    
   def __init__(self, list = None, parent = None):
      Device.__init__(self, list, parent)
      self.Type = ISDN
      self.Dialup = NCDialup.IsdnDialup(None, self)
      
   def load(self, name):
      conf = ConfDevice(name)
      self.Dialup.load(conf)
      
   def createDialup(self):      
      if (self.Dialup == None) \
             or not isinstance(self.Dialup, NCDialup.IsdnDialup):
         self.Dialup = NCDialup.IsdnDialup(None, self)
      return self.Dialup
   
   def getDialog(self):
      return _devIsdnDialog(self).xml.get_widget("Dialog")
    
   def getWizard(self):
      return _devIsdnWizard

   def isType(self, device):
      if device.Type == ISDN:
         return true
      if getDeviceType(device.Device) == ISDN:
         return true
      return false

def setDevIsdnDialog(dialog):
   global _devIsdnDialog
   _devIsdnDialog = dialog
   
def setDevIsdnWizard(wizard):
   global _devIsdnWizard
   _devIsdnWizard = wizard

df = getDeviceFactory()
df.register(DevIsdn, ISDN)
