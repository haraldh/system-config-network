## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
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

import gtk
import gtk.glade
import signal
import os

import string

import sharedtcpip
from netconfpkg.gui.GUI_functions import *
from netconfpkg.plugins import *
from ptpconfig import ptpConfigDialog

from gtk import TRUE
from gtk import FALSE

class iucvConfigDialog(ptpConfigDialog):
    def __init__(self, device):
        ptpConfigDialog.__init__(self, device)

    def hydrate(self):
        ptpConfigDialog.hydrate(self)

        title = _('IUCV Device')

        self.xml.get_widget('Dialog').set_title(title)
                
        if not self.device.Mtu:
            self.device.Mtu = 9216
        self.xml.get_widget('mtuEntry').set_text(str(self.device.Mtu))
        
    def dehydrate(self):
        if not self.device.Mtu:
            self.device.Mtu = 9216

NCDevIUCV.setDevIUCVDialog(iucvConfigDialog)

__author__ = "Harald Hoyer <harald@redhat.com>"
