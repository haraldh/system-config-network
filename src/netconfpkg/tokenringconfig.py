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
import commands

import NCHardwareList
import NC_functions
from deviceconfig import deviceConfigDialog

from gtk import TRUE
from gtk import FALSE


##
## I18N
##
gettext.bindtextdomain(NC_functions.PROGNAME, "/usr/share/locale")
gettext.textdomain(NC_functions.PROGNAME)
_=gettext.gettext

class tokenringConfigDialog(deviceConfigDialog):
    def __init__(self, device, xml_main = None, xml_basic = None):
        glade_file = "tokenringconfig.glade"
        deviceConfigDialog.__init__(self, glade_file,
                                    device, xml_main, xml_basic)    
        self.xml.signal_autoconnect(
            {
            "on_aliasSupportCB_toggled" : self.on_aliasSupportCB_toggled,
            "on_hwAddressCB_toggled" : self.on_hwAddressCB_toggled,
            "on_hwProbeButton_clicked" : self.on_hwProbeButton_clicked,
            })


    def hydrate(self):
        deviceConfigDialog.hydrate(self)
        ecombo = self.xml.get_widget("tokenringDeviceComboBox")
        hwlist = NCHardwareList.getHardwareList()
        (hwcurr, hwdesc) = NC_functions.create_tokenring_combo(hwlist, self.device.Device)
                                        
        if len(hwdesc):
            ecombo.set_popdown_strings(hwdesc)

        widget = self.xml.get_widget("tokenringDeviceEntry")
        if self.device.Device:
            widget.set_text(hwcurr)
        widget.set_position(0)
        
        if self.device.Alias != None:
            self.xml.get_widget("aliasSupportCB").set_active(TRUE)
            self.xml.get_widget("aliasSpinBox").set_value(self.device.Alias)
        else:
            self.xml.get_widget("aliasSupportCB").set_active(FALSE)

        if self.device.HardwareAddress != None:
            self.xml.get_widget("hwAddressCB").set_active(TRUE)
            self.xml.get_widget("hwAddressEntry").set_text(self.device.HardwareAddress)
        else:
            self.xml.get_widget("hwAddressCB").set_active(FALSE)
            self.xml.get_widget("hwAddressEntry").set_sensitive(FALSE)
            self.xml.get_widget("hwProbeButton").set_sensitive(FALSE)

    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        hw = self.xml.get_widget("tokenringDeviceEntry").get_text()
        fields = string.split(hw)
        hw = fields[0]
        self.device.Device = hw
        if self.xml.get_widget("aliasSupportCB").get_active():
            self.device.Alias = self.xml.get_widget("aliasSpinBox").get_value_as_int()
        else:
            self.device.Alias = None
        if self.xml.get_widget("hwAddressCB").get_active():
            self.device.HardwareAddress = self.xml.get_widget("hwAddressEntry").get_text()
        else:
            self.device.HardwareAddress = None

    def on_aliasSupportCB_toggled(self, check):
        self.xml.get_widget("aliasSpinBox").set_sensitive(check["active"])

    def on_hwAddressCB_toggled(self, check):
        self.xml.get_widget("hwAddressEntry").set_sensitive(check["active"])
        self.xml.get_widget("hwProbeButton").set_sensitive(check["active"])

    def on_hwProbeButton_clicked(self, button):
        hwaddr = commands.getoutput("LC_ALL= LANG= /sbin/ip -o link show "+self.device.Device+" | sed 's/.*link\/ether \([[:alnum:]:]*\).*/\\1/'")
        if hwaddr[:6] == 'Device':
            return
        self.device.HardwareAddress = hwaddr
        self.xml.get_widget("hwAddressEntry").set_text(hwaddr)
