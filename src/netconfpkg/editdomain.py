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

import ProfileList

from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class editDomainDialog:
    def __init__(self, Name):
        self.Name = Name

        glade_file = "editdomain.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = "/usr/share/netconf/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")

        self.xml.signal_autoconnect(
            {
            "on_domainNameEntry_insert_text" : (self.on_domainNameEntry_insert_text, ""),
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.mainquit)
        self.load_icon("network.xpm")
        self.setup()
        #self.hydrate()
        
    def load_icon(self, pixmap_file, widget = None):
        if not os.path.exists(pixmap_file):
            pixmap_file = "pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "../pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "/usr/share/netconf/" + pixmap_file
        if not os.path.exists(pixmap_file):
            return

        pix, mask = gtk.create_pixmap_from_xpm(self.dialog, None, pixmap_file)
        gtk.GtkPixmap(pix, mask)

        if widget:
            widget.set(pix, mask)
        else:
            self.dialog.set_icon(pix, mask)
            
    def on_Dialog_delete_event(self, *args):
        self.dialog.destroy()
        
    def on_okButton_clicked(self, button):
        self.dehydrate()
        self.main.hydrate()
        self.dialog.destroy()
        
    def on_cancelButton_clicked(self, button):
        self.dialog.destroy()
        
    def on_domainNameEntry_insert_text(self, entry, partial_text, length,
                                       pos, str):
        pass

    def hydrate(self):
        pass

    def dehydrate(self):
        profilelist = ProfileList.getProfileList()
        
        for prof in profilelist:
            if prof.Active == true:
                index = prof.DNS.SearchList.index(self.Name)
                n = self.xml.get_widget("domainNameEntry").get_text()
                
                if len(string.strip(n)) == 0:
                    del prof.DNS.SearchList[index]
                else:
                    prof.DNS.SearchList[index] = n

                self.hydrate()
                prof.DNS.SearchList.commit()
    
    def setup(self):
        self.xml.get_widget("domainNameEntry").set_text(self.Name)



# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    dialog = editAdressDialog()
    dialog.run()
    gtk.mainloop()

