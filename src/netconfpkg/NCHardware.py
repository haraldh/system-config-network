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

from netconfpkg.NC_functions import _
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties, Gdtstr,
                            Gdtint)

HW_INACTIVE = _("inactive") # not found in last config and not in actual system
HW_SYSTEM = _("system")   # found in system
HW_CONF = _("configured")     # found in config but not in system
HW_OK = _("ok")       # found in system and in config

class Card(Gdtstruct):
    gdtstruct_properties([
                          ('ModuleName', Gdtstr, "Test doc string"),
                          ('Type', Gdtstr, "Test doc string"),
                          ('IoPort', Gdtstr, "Test doc string"),
                          ('IoPort1', Gdtstr, "Test doc string"),
                          ('IoPort2', Gdtstr, "Test doc string"),
                          ('Mem', Gdtstr, "Test doc string"),
                          ('IRQ', Gdtstr, "Test doc string"),
                          ('DMA0', Gdtint, "Test doc string"),
                          ('DMA1', Gdtint, "Test doc string"),
                          ('ChannelProtocol', Gdtstr, "Test doc string"),
                          ('Firmware', Gdtstr, "Test doc string"),
                          ('DriverId', Gdtstr, "Test doc string"),
                          ('VendorId', Gdtstr, "Test doc string"),
                          ('DeviceId', Gdtstr, "Test doc string"),
                          ])
    def __init__(self):
        super(Card, self).__init__()
        self.ModuleName = None
        self.Type = None
        self.IoPort = None
        self.IoPort1 = None
        self.IoPort2 = None
        self.Mem = None
        self.IRQ = None
        self.DMA0 = None
        self.DMA1 = None
        self.ChannelProtocol = None
        self.Firmware = None
        self.DriverId = None
        self.VendorId = None
        self.DeviceId = None

class Hardware_base(Gdtstruct):
    gdtstruct_properties([
                          ('Name', Gdtstr, "Test doc string"),
                          ('Description', Gdtstr, "Test doc string"),
                          ('Type ', Gdtstr, "Test doc string"),
                          ('Status', Gdtstr, "Test doc string"),
                          ('Card', Card, "Test doc string"),
                          ])
    def __init__(self):
        super(Hardware_base, self).__init__()
        self.Name = None
        self.Description = None
        self.Type = None
        self.Card = None
        self.Status = HW_INACTIVE

    def createCard(self):
        if self.Card == None:
            self.Card = Card()
        return self.Card            

class Hardware(Hardware_base):
    def getDialog(self):
        return None

    def getWizard(self):
        return None

    def isType(self, device): # pylint: disable-msg=W0613
        return None

    def save(self, *args, **kwargs): # pylint: disable-msg=W0613
        return None

    def postSave(self):
        return None

__author__ = "Harald Hoyer <harald@redhat.com>"