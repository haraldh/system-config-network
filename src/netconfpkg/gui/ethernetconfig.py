## Copyright (C) 2001, 2002 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001, 2002 Harald Hoyer <harald@redhat.com>
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
import sharedtcpip
import traceback
import sys
from netconfpkg import ethtool
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

class ethernetConfigDialog(deviceConfigDialog):
    def __init__(self, device):
        glade_file = "sharedtcpip.glade"
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file
        self.sharedtcpip_xml = libglade.GladeXML(glade_file, None,
                                                 domain=GUI_functions.PROGNAME)
        glade_file = "ethernetconfig.glade"
        deviceConfigDialog.__init__(self, glade_file,
                                    device)    
        self.xml.signal_autoconnect(
            {
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
        sharedtcpip.route_init (self.sharedtcpip_xml, self.device)

        window = self.sharedtcpip_xml.get_widget ('hardwareWindow')
        frame = self.sharedtcpip_xml.get_widget ('hardwareFrame')
        vbox = self.xml.get_widget ('hardwareVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.hardware_init (self.sharedtcpip_xml, self.device)
        self.hydrate ()

    def hydrate(self):
        deviceConfigDialog.hydrate(self)
        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_hydrate (self.sharedtcpip_xml, self.device)

    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_dehydrate (self.sharedtcpip_xml, self.device)

    def on_aliasSupportCB_toggled(self, check):
        self.xml.get_widget("aliasSpinBox").set_sensitive(check["active"])

    def on_hwAddressCB_toggled(self, check):
        self.xml.get_widget("hwAddressEntry").set_sensitive(check["active"])
        self.xml.get_widget("hwProbeButton").set_sensitive(check["active"])

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
            
