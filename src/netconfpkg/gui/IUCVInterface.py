## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>

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

from netconfpkg.gui.GUI_functions import *
from netconfpkg import *
from netconfpkg.gui import sharedtcpip
import gtk
from gtk import TRUE
from gtk import FALSE
import gtk.glade
import string
import os
#from IUCVHardwareDruid import IUCVHardware
from InterfaceCreator import InterfaceCreator
from rhpl import ethtool
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg.gui.PTPInterface import PTPInterface

class IUCVInterface(PTPInterface):
    def __init__(self, toplevel=None, connection_type=IUCV, do_save = 1,
                 druid = None):
        PTPInterface.__init__(self, toplevel,
                                   connection_type,
                                   do_save, druid)

    def init_gui(self):
        PTPInterface.init_gui(self)
        if not self.device.Mtu:
            self.device.Mtu = 9216

    def get_project_name(self):
        return _('IUCV connection')

    def get_type(self):
        return IUCV
 
    def get_project_description(self):
        return _("Create a new IUCV connection.")

NCDevIUCV.setDevIUCVWizard(IUCVInterface)
__author__ = "Harald Hoyer <harald@redhat.com>"


