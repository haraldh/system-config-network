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
import re

import HardwareList
import tcpdialog

from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class deviceConfigDialog:
    def __init__(self, glade_file, device, xml_main = None, xml_basic = None):
        self.device = device
        self.xml_main = xml_main
        self.xml_basic = xml_basic

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = "/usr/share/redhat-config-network/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")

        self.xml.signal_autoconnect(
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_deviceNameEntry_changed" : self.on_deviceNameEntry_changed,
            "on_deviceNameEntry_insert_text" : (self.on_generic_entry_insert_text,
                                                r"^[a-z|A-Z|0-9]+$"),
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_protocolEditButton_clicked" : self.on_protocolEditButton_clicked,
            })

        self.xml.get_widget("okButton").set_sensitive(len(self.xml.get_widget('deviceNameEntry').get_text()) > 0)
        self.xml.get_widget("protocolList").append(['TCP/IP'])

        self.dialog = self.xml.get_widget("Dialog")
        self.load_icon("network.xpm")        
        self.dialog.set_close(TRUE)

        self.hydrate()

    def load_icon(self, pixmap_file, widget = None):
        if not os.path.exists(pixmap_file):
            pixmap_file = "pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "../pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "/usr/share/redhat-config-network/" + pixmap_file
        if not os.path.exists(pixmap_file):
            return

        pix, mask = gtk.create_pixmap_from_xpm(self.dialog, None, pixmap_file)
        gtk.GtkPixmap(pix, mask)

        if widget:
            widget.set(pix, mask)
        else:
            self.dialog.set_icon(pix, mask)

    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_protocolEditButton_clicked(self, button):
        cfg = tcpdialog.tcpConfigDialog(self.device, self.xml)
        dialog = cfg.xml.get_widget ("Dialog")
        button = dialog.run ()
    
    def on_deviceNameEntry_changed(self, entry):
        deviceName = string.strip(entry.get_text())
        self.device.DeviceId = deviceName
        self.xml.get_widget("okButton").set_sensitive(len(deviceName) > 0)

    def on_okButton_clicked(self, button):
        self.dehydrate()
        
    def on_cancelButton_clicked(self, button):
        pass
    
    def hydrate(self):
        if self.device.DeviceId:
            self.xml.get_widget('deviceNameEntry').set_text(self.device.DeviceId)
                
            self.xml.get_widget('onBootCB').set_active(self.device.OnBoot == TRUE)
            self.xml.get_widget('userControlCB').set_active(self.device.AllowUser == TRUE)


    def dehydrate(self):
        self.device.DeviceId = self.xml.get_widget('deviceNameEntry').get_text()
        self.device.OnBoot = self.xml.get_widget('onBootCB').get_active()
        self.device.AllowUser = self.xml.get_widget('userControlCB').get_active()
