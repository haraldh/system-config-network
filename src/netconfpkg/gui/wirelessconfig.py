## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>
## Preston Brown <pbrown@redhat.com>

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
import sharedtcpip

from netconfpkg import *
from netconfpkg.gui import GUI_functions
from deviceconfig import deviceConfigDialog
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect

from gtk import TRUE
from gtk import FALSE


class wirelessConfigDialog(deviceConfigDialog):
    def __init__(self, device):
        glade_file = "sharedtcpip.glade"
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file
        self.sharedtcpip_xml = gtk.glade.XML(glade_file, None,
                                                 domain=GUI_functions.PROGNAME)

        glade_file = "wirelessconfig.glade"
        deviceConfigDialog.__init__(self, glade_file, device)


        xml_signal_autoconnect(self.xml,
            {
            "on_essidAutoButton_toggled" : self.on_essidAutoButton_toggled,
            })

        self.xml.get_widget("modeEntry").connect("changed",
                                                 self.on_modeChanged)
                                                 
        window = self.sharedtcpip_xml.get_widget ('dhcpWindow')
        frame = self.sharedtcpip_xml.get_widget ('dhcpFrame')
        vbox = self.xml.get_widget ('generalVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.dhcp_init (self.sharedtcpip_xml, self.device)

        window = self.sharedtcpip_xml.get_widget ('hardwareWindow')
        frame = self.sharedtcpip_xml.get_widget ('hardwareFrame')
        vbox = self.xml.get_widget ('hardwareVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.hardware_init (self.sharedtcpip_xml, self.device)
        

    def hydrate(self):
        deviceConfigDialog.hydrate(self)

        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_hydrate (self.sharedtcpip_xml, self.device)

        #ecombo = self.xml.get_widget("ethernetDeviceComboBox")
                    
        #hwlist = NCHardwareList.getHardwareList()
        #(hwcurr, hwdesc) = GUI_functions.create_ethernet_combo(hwlist,self.device.Device)

        #if len(hwdesc):
        #    ecombo.set_popdown_strings(hwdesc)

        #widget = self.xml.get_widget("ethernetDeviceEntry")
        #if self.device.Device and hwcurr:
        #    widget.set_text(hwcurr)
        #widget.set_position(0)
        
        wl = self.device.Wireless
        if wl:
            if wl.Mode: self.xml.get_widget("modeEntry").set_text(wl.Mode)
            
            if wl.EssId == "":
                self.xml.get_widget("essidAutoButton").set_active(TRUE)
                self.xml.get_widget("essidEntry").set_sensitive(FALSE)
            else:
                self.xml.get_widget("essidSpecButton").set_active(TRUE)
                self.xml.get_widget("essidAutoButton").set_active(FALSE)
                self.xml.get_widget("essidEntry").set_sensitive(TRUE)
            if wl.EssId:
                self.xml.get_widget("essidEntry").set_text(wl.EssId)

            if wl.Channel and wl.Channel != "":
                self.xml.get_widget("channelSpinButton").set_value(int(wl.Channel))
            if wl.Rate: self.xml.get_widget("rateEntry").set_text(wl.Rate)
            if wl.Key: self.xml.get_widget("keyEntry").set_text(wl.Key)

        self.on_modeChanged(self.xml.get_widget("modeEntry"))
        self.on_essidAutoButton_toggled(self.xml.get_widget("essidAutoButton"))


    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)

        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_dehydrate (self.sharedtcpip_xml, self.device)

        #hw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        #fields = string.split(hw)
        #hw = fields[0]
        #self.device.Device = hw

        wl = self.device.Wireless
        if wl:
            if self.xml.get_widget("essidAutoButton").get_active():
                wl.EssId = ""
            else:
                wl.EssId = self.xml.get_widget("essidEntry").get_text()
            wl.Mode =  self.xml.get_widget("modeEntry").get_text()            
            
            wl.Channel = str(self.xml.get_widget("channelSpinButton").get_value_as_int())
            wl.Rate = self.xml.get_widget("rateEntry").get_text()
            wl.Key = self.xml.get_widget("keyEntry").get_text()

    def on_essidAutoButton_toggled(self, check):
        self.xml.get_widget("essidEntry").set_sensitive(not check.get_active())

    def on_modeChanged(self, entry):
        if string.lower(entry.get_text()) == "managed":
            self.xml.get_widget("channelSpinButton").set_sensitive(FALSE)
            self.xml.get_widget("rateCombo").set_sensitive(FALSE)
            self.xml.get_widget("rateEntry").set_sensitive(FALSE)
        else:
            self.xml.get_widget("channelSpinButton").set_sensitive(TRUE)
            self.xml.get_widget("rateCombo").set_sensitive(TRUE)
            self.xml.get_widget("rateEntry").set_sensitive(TRUE)
        self.on_essidAutoButton_toggled(self.xml.get_widget("essidAutoButton"))

NCDevWireless.setDevWirelessDialog(wirelessConfigDialog)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/05/16 09:45:00 $"
__version__ = "$Revision: 1.21 $"
