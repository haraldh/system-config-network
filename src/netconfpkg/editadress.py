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
import re

from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class editAdressDialog:
    def __init__(self, xml_main = None, xml_basic = None, list = None):
        self.xml_main = xml_main
        self.xml_basic = xml_basic
        self.list = list

        glade_file = "editadress.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = "/usr/share/netconf/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")

        self.xml.signal_autoconnect(
            {
            "on_addressEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[a-f|0-9\.]"),
            "on_netmaskEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[a-f|0-9\.]"),
            "on_gatewayEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[a-f|0-9\.]"),
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.mainquit)
        pix, mask = gtk.create_pixmap_from_xpm(self.dialog, None,
                                               "pixmaps/network.xpm")
        gtk.GtkPixmap(pix, mask) 
        self.dialog.set_icon(pix, mask)
        self.dialog.show()
        
    def on_Dialog_delete_event(self, *args):
        self.dialog.destroy()
        
    def on_okButton_clicked(self, button):
        self.dialog.destroy()
        
    def on_cancelButton_clicked(self, button):
        self.dialog.destroy()
        
    def on_isdnCardEntry_changed(self, entry):
        pass

    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')
        
    def updateDialog(self):
        pass

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = editAdressDialog()
    gtk.mainloop()

