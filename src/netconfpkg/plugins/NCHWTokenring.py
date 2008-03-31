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

_hwTokenringDialog = None
_hwTokenringWizard = None

class HwTokenring(Hardware):
    def __init__(self, list = None, parent = None):
        Hardware.__init__(self, list, parent)
        self.Type = TOKENRING
        self.createCard()

    def getDialog(self):
        if _hwTokenringDialog == None: return None
        if hasattr(_hwTokenringDialog, "getDialog"):
            return _hwTokenringDialog(self).getDialog()
        return _hwTokenringDialog(self).xml.get_widget("Dialog")

    def getWizard(self):
        return _hwTokenringWizard

    def isType(self, hardware):
        if hardware.Type == TOKENRING:
            return True
        if getHardwareType(hardware.Hardware) == TOKENRING:
            return True
        return False

    def save(self):
        self.saveModule()

def setHwTokenringDialog(dialog):
    global _hwTokenringDialog
    _hwTokenringDialog = dialog

def setHwTokenringWizard(wizard):
    global _hwTokenringWizard
    _hwTokenringWizard = wizard

df = getHardwareFactory()
df.register(HwTokenring, TOKENRING)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/14 09:29:37 $"
__version__ = "$Revision: 1.9 $"
