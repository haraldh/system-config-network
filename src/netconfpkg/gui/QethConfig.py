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

import gtk

import gtk.glade
import signal
import os

import string
import commands
import sharedtcpip
import traceback
import sys
from netconfpkg import *
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from DeviceConfigDialog import DeviceConfigDialog
from rhpl import ethtool

# FIXME: [164594] OK and Cancel buttons on the edit ethernet device window are in reverse order to every other system-config package.

class qethConfigDialog(DeviceConfigDialog):
    def __init__(self, device):
        glade_file = "QethConfig.glade"
        DeviceConfigDialog.__init__(self, glade_file,
                                    device)    

        xml_signal_autoconnect(self.xml, { \
            "on_aliasSupportCB_toggled" : self.on_aliasSupportCB_toggled,
            "on_hwAddressCB_toggled" : self.on_hwAddressCB_toggled,
            "on_hwProbeButton_clicked" : self.on_hwProbeButton_clicked,
            })
                

        window = self.sharedtcpip_xml.get_widget ('dhcpWindow')
        frame = self.sharedtcpip_xml.get_widget ('dhcpFrame')
        vbox = self.xml.get_widget ('generalVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.dhcp_init (self.sharedtcpip_xml, self.device)

        window = self.sharedtcpip_xml.get_widget ('routeWindow')
        frame = self.sharedtcpip_xml.get_widget ('routeFrame')
        vbox = self.xml.get_widget ('routeVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.route_init (self.sharedtcpip_xml, self.device, self.dialog)

        window = self.sharedtcpip_xml.get_widget ('hardwareWindow')
        frame = self.sharedtcpip_xml.get_widget ('hardwareFrame')
        vbox = self.xml.get_widget ('hardwareVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.hardware_init (self.sharedtcpip_xml, self.device)
        self.hydrate ()

    def hydrate(self):
        DeviceConfigDialog.hydrate(self)
        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_hydrate (self.sharedtcpip_xml, self.device)

    def dehydrate(self):
        DeviceConfigDialog.dehydrate(self)
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_dehydrate (self.sharedtcpip_xml, self.device)

    def on_aliasSupportCB_toggled(self, check):
        self.xml.get_widget("aliasSpinBox").set_sensitive(check.get_active())

    def on_hwAddressCB_toggled(self, check):
        self.xml.get_widget("hwAddressEntry").set_sensitive(check.get_active())
        self.xml.get_widget("hwProbeButton").set_sensitive(check.get_active())

    def on_hwProbeButton_clicked(self, button):
        hw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        fields = string.split(hw)
        device = fields[0]
        try: hwaddr = ethtool.get_hwaddr(device) 
        except IOError, err:
            self.error_str = str (err)
            GUI_functions.gui_error_dialog(self.error_str, self.dialog)
        else:
            self.device.HardwareAddress = hwaddr
            self.xml.get_widget("hwAddressEntry").set_text(hwaddr)
            
NCDevQeth.setDevQethDialog(qethConfigDialog)
__author__ = "Harald Hoyer <harald@redhat.com>"