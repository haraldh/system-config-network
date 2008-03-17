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
from netconfpkg import Hardware_base # pylint: disable-msg=E0611

HW_INACTIVE = _("inactive") # not found in last config and not in actual system
HW_SYSTEM = _("system")   # found in system
HW_CONF = _("configured")     # found in config but not in system
HW_OK = _("ok")       # found in system and in config

class Hardware(Hardware_base):
    def __init__(self, clist = None, parent = None):
        Hardware_base.__init__(self, clist, parent)
        self.Status = HW_INACTIVE

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
__date__ = "$Date: 2007/03/14 09:29:37 $"
__version__ = "$Revision: 1.12 $"
