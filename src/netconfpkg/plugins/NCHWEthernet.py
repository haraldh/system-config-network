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

from netconfpkg.NCHardware import Hardware
from netconfpkg.NCHardwareFactory import getHardwareFactory
from netconfpkg.NC_functions import *

_hwEthernetDialog = None
_hwEthernetWizard = None

class HwEthernet(Hardware):    
   def __init__(self, list = None, parent = None):
      Hardware.__init__(self, list, parent)
      self.Type = ETHERNET
      self.createCard()
      
   def getDialog(self):
      if _hwEthernetDialog == None: return None
      return _hwEthernetDialog(self).xml.get_widget("Dialog")
    
   def getWizard(self):
      return _hwEthernetWizard

   def isType(self, hardware):
      if hardware.Type == ETHERNET:
         return true
      if getHardwareType(hardware.Hardware) == ETHERNET:
         return true
      return false

def setHwEthernetDialog(dialog):
   global _hwEthernetDialog
   _hwEthernetDialog = dialog

def setHwEthernetWizard(wizard):
   global _hwEthernetWizard
   _hwEthernetWizard = wizard

df = getHardwareFactory()
df.register(HwEthernet, ETHERNET)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/05/16 09:45:00 $"
__version__ = "$Revision: 1.3 $"
