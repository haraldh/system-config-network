"""Implementation of the iucv device
"""
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

from netconfpkg.NCDevice import Device
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import IUCV
from netconfpkg.plugins.NCDevEthernet import DevEthernet

_devIUCVDialog = None
_devIUCVWizard = None

class DevIUCV(DevEthernet):  
   def __init__(self, list = None, parent = None):
      DevEthernet.__init__(self, list, parent)
      self.Type = IUCV
       
   def isType(self, device):
      """returns true of the device is of the same type as this class"""
      if device.Type == IUCV:
         return true
      if getDeviceType(device.Device) == IUCV:
         return true
      return false


   def load(self, name):
      Device.load(self, name)
      if not self.Mtu:
         self.Mtu = 9216

   def save(self):
      if not self.Mtu:
         self.Mtu = 9216      
      Device.save(self)

   def getDialog(self):
      """get the gtk.Dialog of the iucv configuration dialog"""
      return _devIUCVDialog(self).xml.get_widget("Dialog")
    
   def getWizard(self):
      """get the wizard of the iucv wizard"""
      return _devIUCVWizard

def setDevIUCVDialog(dialog):
   """Set the iucv dialog class"""
   global _devIUCVDialog
   _devIUCVDialog = dialog

def setDevIUCVWizard(wizard):
   """Set the iucv wizard class"""
   global _devIUCVWizard
   _devIUCVWizard = wizard


import os
machine = os.uname()[4]
if machine == 's390' or machine == 's390x' \
       or os.path.isfile("/etc/chandev.conf"):
   _df = getDeviceFactory()
   _df.register(DevIUCV, IUCV)
   del _df
   
__author__ = "Harald Hoyer <harald@redhat.com>"


