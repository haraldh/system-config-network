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

from netconfpkg.NCDevice import *
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import *

_devCipeDialog = None
_devCipeWizard = None

class DevCipe(Device):
    def __init__(self, list = None, parent = None):
        Device.__init__(self, list, parent)
        self.Type = CIPE
        self.createCipe()

    def load(self, name):
        conf = ConfDevice(name)
        Device.load(self, name)
        self.Cipe.load(conf)

    def checkSystem(self):
        pass

    def createCipe(self):
        Device.createCipe(self)
        return self.Cipe

    def getDialog(self):
        dialog =  _devCipeDialog(self)
        if hasattr(dialog, "xml"):
            return dialog.xml.get_widget("Dialog")

        return dialog

    def getWizard(self):
        return _devCipeWizard

    def isType(self, device):
        if device.Type == CIPE:
            return True
        if getDeviceType(device.Device) == CIPE:
            return True
        return False

    def getHWDevice(self):
        if self.Cipe:
            return self.Cipe.TunnelDevice
        return None

def setDevCipeDialog(dialog):
    global _devCipeDialog
    _devCipeDialog = dialog

def setDevCipeWizard(wizard):
    global _devCipeWizard
    _devCipeWizard = wizard

if NC_functions.DOCIPE:
    df = getDeviceFactory()
    df.register(DevCipe, CIPE)

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/14 09:29:37 $"
__version__ = "$Revision: 1.11 $"
