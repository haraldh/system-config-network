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

import sys
sys.path.append("/usr/lib/rhs/python/")

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
import Conf

from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class ethernetHardwareDialog:
    def __init__(self, xml_main = None):
        self.xml_main = xml_main

        glade_file = "ethernethardware.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = "/usr/share/netconf/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")

        self.xml.signal_autoconnect(
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_adapterEntry_changed" : self.on_adapterEntry_changed
            })

        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.mainquit)
        self.load_icon("network.xpm")
        self.updateDialog()
        self.dialog.show()
        
    def on_Dialog_delete_event(self, *args):
        self.dialog.destroy()
        
    def on_okButton_clicked(self, button):
        idx = -1
        pos = 0
        for hw in self.hardwarelist:
            if hw.Name == self.xml.get_widget('ethernetDeviceEntry').get_text():
                idx = pos
            pos = pos+1

        if idx == -1:
            idx = self.hardwarelist.addHardware()

        hw = self.hardwarelist[idx]

        hw.Name = self.xml.get_widget('ethernetDeviceEntry').get_text()
        hw.Description = self.xml.get_widget('adapterEntry').get_text()
        hw.Type = 'Ethernet'
        hw.createCard()
        print self.xml.get_widget('adapterComboBox').list
        hw.Card.ModuleName = ''

        self.main.setup()
        self.dialog.destroy()

    def on_cancelButton_clicked(self, button):
        self.dialog.destroy()

    def on_adapterEntry_changed(self, entry):
        pass

    def load_icon(self, pixmap_file, widget = None):
        if not os.path.exists(pixmap_file):
            pixmap_file = "../pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "pixmaps/" + pixmap_file
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
            
    def updateDialog(self):
        list = []
        modInfo = Conf.ConfModInfo()
        for i in modInfo.keys():
            if modInfo[i]['type'] == "eth":
                list.append(modInfo[i]['description'])
        self.xml.get_widget("adapterComboBox").set_popdown_strings(list)




# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = ethernetHardwareDialog()
    gtk.mainloop()

