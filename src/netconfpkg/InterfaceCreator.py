## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Than Ngo <than@redhat.com>
## Copyright (C) 2001 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001 Philipp Knirsch <pknirsch@redhat.com>

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

from NCDeviceList import *
from NCDevice import *
from NCProfileList import *
from NCHardwareList import *

class InterfaceCreator:
    def __init__ (self):
        raise NotImplementedError

    def get_project_name (self):
        raise NotImplementedError

    def get_project_description (self):
        raise NotImplementedError

    def get_druids (self):
        raise NotImplementedError

    def finish (self):
        raise NotImplementedError

    def save(self):
        self.saveDevices()
        self.saveHardware()
        self.saveProfiles()

    def saveDevices(self):
        devicelist = getDeviceList()
        devicelist.save()

    def saveHardware(self):
        hardwarelist = getHardwareList()
        hardwarelist.save()

    def saveProfiles(self):
        profilelist = getProfileList()
        profilelist.save()
