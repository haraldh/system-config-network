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
import sharedtcpip

from netconfpkg import NCHardwareList
from netconfpkg.gui import GUI_functions
from netconfpkg.NC_functions import _
from deviceconfig import deviceConfigDialog
from gtk import TRUE
from gtk import FALSE


class dslConfigDialog(deviceConfigDialog):
    def __init__(self, device):
        glade_file = "sharedtcpip.glade"
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file
        self.sharedtcpip_xml = libglade.GladeXML (glade_file, None)

        glade_file = "dslconfig.glade"
        deviceConfigDialog.__init__(self, glade_file,
                                    device)

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
        dialup = self.device.Dialup
        widget = self.xml.get_widget("providerNameEntry")
        if dialup.ProviderName:
            widget.set_text(dialup.ProviderName)
        widget.set_position(0)

        widget = self.xml.get_widget("loginNameEntry")
        if dialup.Login:
            widget.set_text(dialup.Login)
        widget.set_position(0)

        widget =  self.xml.get_widget("passwordEntry")
        if dialup.Password:
            widget.set_text(dialup.Password)
        widget.set_position(0)

        widget = self.xml.get_widget("serviceNameEntry")
        if dialup.ServiceName:
            widget.set_text(dialup.ServiceName)
        widget.set_position(0)

        widget = self.xml.get_widget("acNameEntry")
        if dialup.AcName:
            widget.set_text(dialup.AcName)
        widget.set_position(0)

        self.xml.get_widget("useSyncpppCB").set_active(dialup.SyncPPP == TRUE)
        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_hydrate (self.sharedtcpip_xml, self.device)

    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        dialup = self.device.Dialup
        dialup.ProviderName = self.xml.get_widget("providerNameEntry").get_text()
        dialup.Login = self.xml.get_widget("loginNameEntry").get_text()
        dialup.Password = self.xml.get_widget("passwordEntry").get_text()
        dialup.ServiceName = self.xml.get_widget("serviceNameEntry").get_text()
        dialup.AcName = self.xml.get_widget("acNameEntry").get_text()
        dialup.SyncPPP = self.xml.get_widget("useSyncpppCB").get_active()
        if not self.device.Device:
            self.device.Device = "dsl"
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_dehydrate (self.sharedtcpip_xml, self.device)
        

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    dslConfigDialog()
    gtk.mainloop()
