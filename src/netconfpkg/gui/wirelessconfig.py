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

from netconfpkg import NCHardwareList
from netconfpkg.gui import GUI_functions
from deviceconfig import deviceConfigDialog

from gtk import TRUE
from gtk import FALSE

##
## I18N
##
gettext.bindtextdomain(GUI_functions.PROGNAME, "/usr/share/locale")
gettext.textdomain(GUI_functions.PROGNAME)
_=gettext.gettext

class wirelessConfigDialog(deviceConfigDialog):
    def __init__(self, device):
        glade_file = "wirelessconfig.glade"
        deviceConfigDialog.__init__(self, glade_file, device)


        self.xml.get_widget("modeCombo").set_popdown_strings( [ 'auto',
                                                                'Managed',
                                                                'Ad-Hoc',
                                                                'Master',
                                                                'Repeater',
                                                                'Secondary',
                                                                ])

    def hydrate(self):
        deviceConfigDialog.hydrate(self)
        ecombo = self.xml.get_widget("ethernetDeviceComboBox")
                    
        hwlist = NCHardwareList.getHardwareList()
        (hwcurr, hwdesc) = GUI_functions.create_ethernet_combo(hwlist,self.device.Device)

        if len(hwdesc):
            ecombo.set_popdown_strings(hwdesc)

        widget = self.xml.get_widget("ethernetDeviceEntry")
        if self.device.Device and hwcurr:
            widget.set_text(hwcurr)
        widget.set_position(0)
        
        wl = self.device.Wireless
        if wl:
            if wl.EssId: self.xml.get_widget("essidEntry").set_text(wl.EssId)
            if wl.Mode: self.xml.get_widget("modeEntry").set_text(wl.Mode)
            if wl.Channel and wl.Channel != "":
                self.xml.get_widget("channelSpinButton").set_value(int(wl.Channel))
            if wl.Freq: self.xml.get_widget("frequencyEntry").set_text(wl.Freq)
            if wl.Rate: self.xml.get_widget("rateEntry").set_text(wl.Rate)
            if wl.Key: self.xml.get_widget("keyEntry").set_text(wl.Key)


    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        hw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        fields = string.split(hw)
        hw = fields[0]
        self.device.Device = hw

        wl = self.device.Wireless
        if wl:
            wl.EssId = self.xml.get_widget("essidEntry").get_text()
            wl.Mode =  self.xml.get_widget("modeEntry").get_text()
            wl.Channel = str(self.xml.get_widget("channelSpinButton").get_value_as_int())
            wl.Freq = self.xml.get_widget("frequencyEntry").get_text()
            wl.Rate = self.xml.get_widget("rateEntry").get_text()
            wl.Key = self.xml.get_widget("keyEntry").get_text()
