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

from netconfpkg.NCHardware import Hardware
from netconfpkg.NCHardwareFactory import getHardwareFactory
from netconfpkg.NC_functions import *

_hwEthernetDialog = None
_hwEthernetWizard = None

class HwWireless(Hardware):    
   def __init__(self, list = None, parent = None):
      Hardware.__init__(self, list, parent)
      self.Type = WIRELESS
      self.createCard()
      
   def getDialog(self):
      if _hwEthernetDialog == None: return None
      return _hwEthernetDialog(self).xml.get_widget("Dialog")
    
   def getWizard(self):
      return _hwEthernetWizard

   def isType(self, hardware):
      if hardware.Type == WIRELESS:
         return true
      if getHardwareType(hardware.Hardware) == WIRELESS:
         return true
      return false

def setHwWirelessDialog(dialog):
   global _hwEthernetDialog
   _hwEthernetDialog = dialog

def setHwWirelessWizard(wizard):
   global _hwEthernetWizard
   _hwEthernetWizard = wizard

df = getHardwareFactory()
df.register(HwWireless, WIRELESS)
