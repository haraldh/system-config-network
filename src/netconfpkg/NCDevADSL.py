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

from netconfpkg.NCDevice import *
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import *

from netconfpkg import NCDialup

_devADSLDialog = None
_devADSLWizard = None

class DevADSL(Device):    
   def __init__(self, list = None, parent = None):
      Device.__init__(self, list, parent)
      self.Type = DSL
      self.Dialup = NCDialup.DslDialup(None, self)

   def load(self, name):
      conf = ConfDevice(name)
      Device.load(self, name)
      self.Dialup.load(conf)
      
   def createDialup(self):
      if (self.Dialup == None) \
             or not isinstance(self.Dialup, NCDialup.DslDialup):
         self.Dialup = NCDialup.DslDialup(None, self)
      return self.Dialup
      
   def getDialog(self):
      return _devADSLDialog(self).xml.get_widget("Dialog")
   
   def getWizard(self):
      return _devADSLWizard
   
   def isType(self, device):
      if device.Type == DSL:
         return true
      if getDeviceType(device.Device) == DSL:
         return true
      return false
   
def setDevADSLDialog(dialog):
   global _devADSLDialog
   _devADSLDialog = dialog

def setDevADSLWizard(wizard):
   global _devADSLWizard
   _devADSLWizard = wizard

df = getDeviceFactory()
df.register(DevADSL, DSL)
