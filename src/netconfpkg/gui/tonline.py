## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>

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
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect

from gtk import TRUE
from gtk import FALSE


class TonlineDialog:
    def __init__(self, login, pw):
        self.login = login
        self.password = pw
        
        glade_file = "tonline.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            "on_AKEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[0-9]"),
            "on_ZNEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[0-9]"),
            "on_pwEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[0-9]"),
            "on_mbnEntry_insert_text" : \
            (self.on_generic_entry_insert_text, r"^[0-9]"),
            "on_AKEntry_changed" : (self.on_generic_entry_changed, 12),
            "on_ZNEntry_changed" : (self.on_generic_entry_changed, 12),
            "on_pwEntry_changed" : (self.on_generic_entry_changed, 8),
            "on_mbnEntry_changed" : (self.on_generic_entry_changed, 4),
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        #self.xml.get_widget ("addressPixmap").set_from_file(GUI_functions.NETCONFDIR+"pixmaps/network.xpm")
        self.dialog = self.xml.get_widget("Dialog")
        #self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        #self.dialog.connect("hide", gtk.mainquit)
        
        self.hydrate()

    def on_okButton_clicked(self, button):
        self.dehydrate()
    
    def on_cancelButton_clicked(self, button):
        pass

    def check(self):
        if len(self.xml.get_widget('AKEntry').get_text()) < 12 or \
           len(self.xml.get_widget('ZNEntry').get_text()) < 12 or \
           len(self.xml.get_widget('mbnEntry').get_text()) < 4 or \
           len(self.xml.get_widget('pwEntry').get_text()) < 8:
            self.xml.get_widget('okButton').set_sensitive(FALSE)
        else:
            self.xml.get_widget('okButton').set_sensitive(TRUE)
    
    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
            
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')


    def on_generic_entry_changed(self, entry, minlen):
        if len(entry.get_text()) < minlen:
            self.xml.get_widget('okButton').set_sensitive(FALSE)

        self.check()
            
    def hydrate(self):
        self.xml.get_widget('AKEntry').set_text(self.login[0:12])
        self.xml.get_widget('ZNEntry').set_text(self.login[12:24])
        self.xml.get_widget('mbnEntry').set_text(self.login[25:29])
        self.xml.get_widget('pwEntry').set_text(self.password)
        self.check()
        pass

    def dehydrate(self):
        self.login = "%s%s#%s@t-online.de" % \
                     (self.xml.get_widget('AKEntry').get_text(),
                      self.xml.get_widget('ZNEntry').get_text(),
                      self.xml.get_widget('mbnEntry').get_text())
        
        self.password = self.xml.get_widget('pwEntry').get_text()
        
        pass
