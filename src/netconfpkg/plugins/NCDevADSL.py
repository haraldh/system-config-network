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

from netconfpkg.NCDevice import Device, ConfDevice
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import DSL, getDeviceType
import netconfpkg.NCDialup

_devADSLDialog = None
_devADSLWizard = None

class DevADSL(Device):
    def __init__(self, clist = None, parent = None):
        Device.__init__(self, clist, parent)
        self.Type = DSL
        self.Dialup = netconfpkg.NCDialup.DslDialup(None, self)

    def load(self, *args, **kwargs): # pylint: disable-msg=W0613
        name = args[0]
        conf = ConfDevice(name)
        Device.load(self, name)
        self.Dialup.load(conf)

    def createDialup(self):
        if (self.Dialup == None) \
               or not isinstance(self.Dialup, netconfpkg.NCDialup.DslDialup):
            self.Dialup = netconfpkg.NCDialup.DslDialup(None, self)
        return self.Dialup

    def getDialog(self):
        if not _devADSLDialog:
            return None
        dialog =  _devADSLDialog(self)
        if hasattr(dialog, "xml"):
            return dialog.xml.get_widget("Dialog")

        return dialog

    def getWizard(self):
        return _devADSLWizard

    def isType(self, device):
        if device.Type == DSL:
            return True
        if getDeviceType(device.Device) == DSL:
            return True
        return False

    def getHWDevice(self):
        if self.Dialup:
            return self.Dialup.EthDevice # pylint: disable-msg=E1101
        return None

def setDevADSLDialog(dialog):
    global _devADSLDialog
    _devADSLDialog = dialog

def setDevADSLWizard(wizard):
    global _devADSLWizard
    _devADSLWizard = wizard

df = getDeviceFactory()
df.register(DevADSL, DSL)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/14 09:29:37 $"
__version__ = "$Revision: 1.11 $"
