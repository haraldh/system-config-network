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
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from netconfpkg.NCHardware import Hardware
from netconfpkg.NCHardwareFactory import getHardwareFactory
from netconfpkg.NC_functions import *

_hwLcsDialog = None
_hwLcsWizard = None

class HwLcs(Hardware):
   def __init__(self, list = None, parent = None):
      Hardware.__init__(self, list, parent)
      self.Type = LCS
      self.createCard()
      self.Description = "LCS Device"

   def getDialog(self):
      if _hwLcsDialog == None: return None
      if hasattr(_hwLcsDialog, 'getDialog'):
         return _hwLcsDialog(self).getDialog()
      return _hwLcsDialog(self).xml.get_widget("Dialog")

   def getWizard(self):
      return _hwLcsWizard

   def save(self):
      from netconfpkg.NCHardwareList import getMyConfModules, getHardwareList

      modules = getMyConfModules()
      dic = modules[self.Name]
      dic['alias'] = self.Card.ModuleName
      modules[self.Name] = dic

   def isType(self, hardware):
      if hardware.Type == LCS:
         return True
      if getHardwareType(hardware.Hardware) == LCS:
         return True
      return False

def setHwLcsDialog(dialog):
   global _hwLcsDialog
   _hwLcsDialog = dialog

def setHwLcsWizard(wizard):
   global _hwLcsWizard
   _hwLcsWizard = wizard

import os
machine = os.uname()[4]
if machine == 's390' or machine == 's390x':
   df = getHardwareFactory()
   df.register(HwLcs, LCS)

__author__ = "Harald Hoyer <harald@redhat.com>"


