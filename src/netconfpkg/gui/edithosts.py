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
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect

from gtk import TRUE
from gtk import FALSE

class editHostsDialog:
    def __init__(self, host):
        self.host = host

        glade_file = "edithosts.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            "on_addressEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[a-f:0-9\.]"),
            "on_hostnameEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[A-Za-z\-0-9\.]"),
            "on_aliasesEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[A-Za-z\- 0-9\.]"),
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        load_icon("network.xpm", self.dialog)
        
        self.hydrate()

    def on_Dialog_delete_event(self, *args):
        pass

    def on_okButton_clicked(self, button):
        self.dehydrate()
        #self.host.commit()

    def on_cancelButton_clicked(self, button):
        pass

    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def hydrate(self):
        if self.host.IP:
            self.xml.get_widget('addressEntry').set_text(self.host.IP)
        if self.host.Hostname:
            self.xml.get_widget('hostnameEntry').set_text(self.host.Hostname)
        if self.host.AliasList:
            self.xml.get_widget('aliasesEntry').set_text(string.join(self.host.AliasList, ' '))

    def dehydrate(self):
        self.host.IP = self.xml.get_widget('addressEntry').get_text()
        self.host.Hostname = self.xml.get_widget('hostnameEntry').get_text()
        self.host.AliasList = None
        self.host.createAliasList()
        for al in string.split(self.xml.get_widget('aliasesEntry').get_text(), ' '):
            self.host.AliasList.append(al)

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = editHostsDialog()
    gtk.mainloop()
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/05/16 09:45:00 $"
__version__ = "$Revision: 1.11 $"
