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
import re

import tcpdialog
import NC_functions

from gtk import TRUE
from gtk import FALSE

##
## I18N
##
gettext.bindtextdomain(NC_functions.PROGNAME, "/usr/share/locale")
gettext.textdomain(NC_functions.PROGNAME)
_=gettext.gettext

class deviceConfigDialog:
    def __init__(self, glade_file, device, xml_main = None, xml_basic = None):
        self.device = device
        self.xml_main = xml_main
        self.xml_basic = xml_basic

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = NC_functions.NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain=NC_functions.PROGNAME)

        self.xml.signal_autoconnect(
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_deviceNameEntry_changed" : self.on_deviceNameEntry_changed,
            "on_deviceNameEntry_insert_text" : (self.on_generic_entry_insert_text,
                                                r"^[a-z|A-Z|0-9]+$"),
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_protocolEditButton_clicked" : self.on_protocolEditButton_clicked,
            "on_protocolList_button_press_event" : (self.on_generic_clist_button_press_event,
                                                    self.on_protocolEditButton_clicked)
            })

        self.xml.get_widget("okButton").set_sensitive(len(self.xml.get_widget('deviceNameEntry').get_text()) > 0)
        self.xml.get_widget("protocolList").append(['TCP/IP'])

        self.dialog = self.xml.get_widget("Dialog")
        NC_functions.load_icon("network.xpm", self.dialog)
        self.dialog.set_close(TRUE)

        self.hydrate()


    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_protocolEditButton_clicked(self, *args):
        cfg = tcpdialog.tcpConfigDialog(self.device, self.xml)
        dialog = cfg.xml.get_widget ("Dialog")
        button = dialog.run ()

    def on_generic_clist_button_press_event(self, clist, event, func):
        if event.type == GDK._2BUTTON_PRESS:
            info = clist.get_selection_info(event.x, event.y)
            if info != None:
                id = clist.signal_connect("button_release_event",
                                          self.on_generic_clist_button_release_event,
                                          func)
                clist.set_data("signal_id", id)

    def on_generic_clist_button_release_event(self, clist, event, func):
        id = clist.get_data ("signal_id")
        clist.disconnect (id)
        clist.remove_data ("signal_id")
        apply (func)
        
    def on_deviceNameEntry_changed(self, entry):
        deviceName = string.strip(entry.get_text())
        self.device.DeviceId = deviceName
        self.xml.get_widget("okButton").set_sensitive(len(deviceName) > 0)
        self.device.commit()
        
    def on_okButton_clicked(self, button):
        self.dehydrate()
        
    def on_cancelButton_clicked(self, button):
        pass

    def hydrate(self):
        widget = self.xml.get_widget('deviceNameEntry')
        widget.grab_focus()
        if self.device.DeviceId:
            widget.set_text(self.device.DeviceId)
                
            self.xml.get_widget('onBootCB').set_active(self.device.OnBoot == TRUE)
            self.xml.get_widget('userControlCB').set_active(self.device.AllowUser == TRUE)


    def dehydrate(self):
        self.device.DeviceId = self.xml.get_widget('deviceNameEntry').get_text()
        self.device.OnBoot = self.xml.get_widget('onBootCB').get_active()
        self.device.AllowUser = self.xml.get_widget('userControlCB').get_active()
