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

import gtk
import gtk.glade
import signal
import os

import string
import string

from netconfpkg.gui.GUI_functions import *
from deviceconfig import deviceConfigDialog

from gtk import TRUE
from gtk import FALSE

class ctcConfigDialog(deviceConfigDialog):
    def __init__(self, device):
        glade_file = 'ctcconfig.glade'
        deviceConfigDialog.__init__(self, glade_file,
                                    device)

    def hydrate(self):
        deviceConfigDialog.hydrate(self)
        ecombo = self.xml.get_widget("deviceComboBox")
        dlist = []
        title = ''
        if self.device.Type == CTC:
            dlist = ctcDeviceList
            title = _('CTC Device')
        elif self.device.Type == IUCV:
            dlist = iucvDeviceList
            title = _('IUCV Device')

        self.xml.get_widget('Dialog').set_title(title)
        ecombo.set_popdown_strings(dlist)
        
        widget = self.xml.get_widget('deviceEntry')
        if self.device.Device:
            widget.set_text(self.device.Device)
            #widget.set_position(0)
        
        if not self.device.Mtu:
            self.device.Mtu = 1492
        self.xml.get_widget('mtuEntry').set_text(str(self.device.Mtu))

        self.device.BootProto = 'static'
        
    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        self.device.Device = self.xml.get_widget('deviceEntry').get_text()
        self.device.Mtu = str(self.xml.get_widget('mtuEntry').get_text())
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/07/08 09:45:48 $"
__version__ = "$Revision: 1.11 $"
