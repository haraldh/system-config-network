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

from netconfpkg.NCHardware import Hardware
from netconfpkg.NCHardwareFactory import getHardwareFactory
from netconfpkg.NC_functions import *

_hwCTCDialog = None
_hwCTCWizard = None

class HwCTC(Hardware):    
   def __init__(self, list = None, parent = None):
      Hardware.__init__(self, list, parent)
      self.Type = CTC
      self.createCard()
      self.Description = "CTC Device"
      
   def getDialog(self):
      if _hwCTCDialog == None: return None
      if hasattr(_hwCTCDialog, getDialog):
         return _hwCTCDialog(self).getDialog()
      return _hwCTCDialog(self).xml.get_widget("Dialog")
    
   def getWizard(self):
      return _hwCTCWizard

   def isType(self, hardware):
      if hardware.Type == CTC:
         return true
      if getHardwareType(hardware.Hardware) == CTC:
         return true
      return false

def setHwCTCDialog(dialog):
   global _hwCTCDialog
   _hwCTCDialog = dialog

def setHwCTCWizard(wizard):
   global _hwCTCWizard
   _hwCTCWizard = wizard

import os
machine = os.uname()[4]
if machine == 's390' or machine == 's390x' \
       or os.path.isfile("/etc/chandev.conf"):
   df = getHardwareFactory()
   df.register(HwCTC, CTC)
   
__author__ = "Harald Hoyer <harald@redhat.com>"


