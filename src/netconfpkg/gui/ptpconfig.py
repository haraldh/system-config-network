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
from deviceconfig import deviceConfigDialog

from gtk import TRUE
from gtk import FALSE

class ptpConfigDialog(deviceConfigDialog):
    def __init__(self, device):
        glade_file = "ptpconfig.glade"
        deviceConfigDialog.__init__(self, glade_file,
                                    device)

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
        deviceConfigDialog.hydrate(self)
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_hydrate (self.sharedtcpip_xml, self.device)
                
        if self.device.IP:
            self.xml.get_widget('ipAddressEntry').set_text(self.device.IP)
        else:
            self.xml.get_widget('ipAddressEntry').set_text('')

        if self.device.Gateway:
            self.xml.get_widget('ipGatewayEntry').set_text(self.device.Gateway)
        else:
            self.xml.get_widget('ipGatewayEntry').set_text('')

        if self.device.Mtu:
            self.xml.get_widget('mtuEntry').set_text(str(self.device.Mtu))
        else:
            self.xml.get_widget('mtuEntry').set_text('')
            
        self.device.BootProto = 'static'
        
    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_dehydrate (self.sharedtcpip_xml, self.device)

        #self.device.Device = self.xml.get_widget('deviceEntry').get_text()
        self.device.IP = self.xml.get_widget('ipAddressEntry').get_text()
        self.device.Gateway = self.xml.get_widget('ipGatewayEntry').get_text()
        try:
            self.device.Mtu = int(self.xml.get_widget('mtuEntry').get_text())
        except:            
            pass

__author__ = "Harald Hoyer <harald@redhat.com>"
