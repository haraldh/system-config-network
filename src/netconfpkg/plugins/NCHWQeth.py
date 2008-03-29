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

_hwQethDialog = None
_hwQethWizard = None

class HwQeth(Hardware):     
    def __init__(self, list = None, parent = None):
        Hardware.__init__(self, list, parent)
        self.Type = QETH
        self.createCard()
        self.Description = "Qeth Device"
        
    def getDialog(self):
        if _hwQethDialog == None: return None
        if hasattr(_hwQethDialog, 'getDialog'):
            return _hwQethDialog(self).getDialog()
        return _hwQethDialog(self).xml.get_widget("Dialog")
     
    def getWizard(self):
        return _hwQethWizard

    def save(self):
        from netconfpkg.NCHardwareList import getMyConfModules, getHardwareList

        modules = getMyConfModules()
        dic = modules[self.Name]
        dic['alias'] = self.Card.ModuleName
        modules[self.Name] = dic

    def isType(self, hardware):
        if hardware.Type == QETH:
            return true
        if getHardwareType(hardware.Hardware) == QETH:
            return true
        return false

def setHwQethDialog(dialog):
    global _hwQethDialog
    _hwQethDialog = dialog

def setHwQethWizard(wizard):
    global _hwQethWizard
    _hwQethWizard = wizard

import os
machine = os.uname()[4]
if machine == 's390' or machine == 's390x':
    df = getHardwareFactory()
    df.register(HwQeth, QETH)
    
__author__ = "Harald Hoyer <harald@redhat.com>"


