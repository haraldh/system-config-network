#! /usr/bin/python

## netconf - A network configuration tool
## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Than Ngo <than@redhat.com>
 
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
import GDK
import GTK
import libglade
import signal
import os
import GdkImlib
import string
import gettext
import string

import HardwareList
import NC_functions
from deviceconfig import deviceConfigDialog

from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class wirelessConfigDialog(deviceConfigDialog):
    def __init__(self, device, xml_main = None, xml_basic = None):
        glade_file = "wirelessconfig.glade"
        deviceConfigDialog.__init__(self, glade_file,
                                    device, xml_main, xml_basic)    
        self.xml.signal_autoconnect(
            {
            "on_aliasSupportCB_toggled" : self.on_aliasSupportCB_toggled,
            })


    def hydrate(self):
        deviceConfigDialog.hydrate(self)
        ecombo = self.xml.get_widget("ethernetDeviceComboBox")
                    
        hwlist = HardwareList.getHardwareList()
        (hwcurr, hwdesc) = NC_functions.create_ethernet_combo(hwlist,self.device.Device)

        if len(hwdesc):
            ecombo.set_popdown_strings(hwdesc)

        widget = self.xml.get_widget("ethernetDeviceEntry")
        if self.device.Device:
            widget.set_text(hwcurr)
        widget.set_position(0)
        
        if self.device.Alias != None:
            self.xml.get_widget("aliasSupportCB").set_active(TRUE)
            self.xml.get_widget("aliasSpinBox").set_value(self.device.Alias)
        else:
            self.xml.get_widget("aliasSupportCB").set_active(FALSE)


    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        hw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        fields = string.split(hw)
        hw = fields[0]
        self.device.Device = hw
        if self.xml.get_widget("aliasSupportCB").get_active():
            self.device.Alias = self.xml.get_widget("aliasSpinBox").get_value_as_int()
        else: self.device.Alias = None
    
    def on_aliasSupportCB_toggled(self, check):
        self.xml.get_widget("aliasSpinBox").set_sensitive(check["active"])
