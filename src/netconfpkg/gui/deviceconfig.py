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

import gtk
import gtk.glade
import signal
import os

import string
import re

from netconfpkg.gui.GUI_functions import *
from netconfpkg import nop
from netconfpkg import NCDeviceList

from gtk import TRUE
from gtk import FALSE

class deviceConfigDialog:
    def __init__(self, glade_file, device):
        self.device = device

        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=PROGNAME)
        self.dialog = self.xml.get_widget("Dialog")
        xml_signal_autoconnect(self.xml,
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_deviceNameEntry_changed" : self.on_deviceNameEntry_changed,
            "on_deviceNameEntry_insert_text" : (self.on_generic_entry_insert_text,
                                                r"^[a-z|A-Z|0-9\_:]+$"),
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            })

        self.xml.get_widget("okButton").set_sensitive(len(self.xml.get_widget('deviceNameEntry').get_text()) > 0)

        load_icon("network.xpm", self.dialog)
        #

        self.hydrate()


    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_generic_clist_button_press_event(self, clist, event, func):
        if event.type == gtk.gdk._2BUTTON_PRESS:
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
        
    def on_okButton_clicked(self, button):
        self.dehydrate()
        devicelist = NCDeviceList.getDeviceList()
        for dev in devicelist:
            if dev == self.device:
                continue
            if dev.DeviceId == self.device.DeviceId:
                generic_error_dialog (\
                _("Nickname %s is already in use!\nPlease choose another one.\n") \
                                      % (self.device.DeviceId))
                duplicate = TRUE
                num = 0
                while duplicate:
                    devname = self.device.DeviceId + '_' + str(num)
                    duplicate = FALSE
                    for dev in devicelist:
                        if dev.DeviceId == devname:
                            duplicate = TRUE
                            break
                    num = num + 1
                self.device.DeviceId = devname
                break
        
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
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/06/18 11:06:57 $"
__version__ = "$Revision: 1.14 $"
