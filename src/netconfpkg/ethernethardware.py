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
    def __init__(self, hw, xml_main = None):
        self.hw = hw
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
        self.dialog.set_close(TRUE)
        self.setup()
        self.hydrate()

    def on_Dialog_delete_event(self, *args):
        pass

    def on_okButton_clicked(self, button):
        self.dehydrate()
        self.hw.commit()

    def on_cancelButton_clicked(self, button):
        pass

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

    def hydrate(self):
        if self.hw.Name:
            self.xml.get_widget('ethernetDeviceEntry').set_text(self.hw.Name)
            self.xml.get_widget('adapterEntry').set_text(self.hw.Description)
            self.xml.get_widget('adapterEntry').set_sensitive(FALSE)
            self.xml.get_widget('adapterComboBox').set_sensitive(FALSE)
            if self.hw.Card.IRQ:
                self.xml.get_widget('irqEntry').set_text(self.hw.Card.IRQ)
            if self.hw.Card.Mem:
                self.xml.get_widget('memEntry').set_text(self.hw.Card.Mem)
            if self.hw.Card.IoPort:
                self.xml.get_widget('ioEntry').set_text(self.hw.Card.IoPort)
            if self.hw.Card.IoPort1:
                self.xml.get_widget('io1Entry').set_text(self.hw.Card.IoPort1)
            if self.hw.Card.IoPort2:
                self.xml.get_widget('io2Entry').set_text(self.hw.Card.IoPort2)
            if self.hw.Card.DMA0:
                self.xml.get_widget('dma0Entry').set_text(self.hw.Card.DMA0)
            if self.hw.Card.DMA1:
                self.xml.get_widget('dma1Entry').set_text(self.hw.Card.DMA1)

    def setup(self):
        list = []
        modInfo = Conf.ConfModInfo()
        for i in modInfo.keys():
            if modInfo[i]['type'] == "eth":
                list.append(modInfo[i]['description'])
        list.sort()
        self.xml.get_widget("adapterComboBox").set_popdown_strings(list)

    def dehydrate(self):
        self.hw.Name = self.xml.get_widget('ethernetDeviceEntry').get_text()
        self.hw.Description = self.xml.get_widget('adapterEntry').get_text()
        self.hw.Type = 'Ethernet'
        self.hw.createCard()
        self.hw.Card.IRQ = self.xml.get_widget('irqEntry').get_text()
        self.hw.Card.Mem = self.xml.get_widget('memEntry').get_text()
        self.hw.Card.IoPort = self.xml.get_widget('ioEntry').get_text()
        self.hw.Card.IoPort1 = self.xml.get_widget('io1Entry').get_text()
        self.hw.Card.IoPort2 = self.xml.get_widget('io2Entry').get_text()
        self.hw.Card.DMA0 = self.xml.get_widget('dma0Entry').get_text()
        self.hw.Card.DMA1 = self.xml.get_widget('dma1Entry').get_text()
        modInfo = Conf.ConfModInfo()
        self.hw.Card.ModuleName = 'Unknown'
        for i in modInfo.keys():
            if modInfo[i]['description'] == self.hw.Description:
                self.hw.Card.ModuleName = i

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = ethernetHardwareDialog()
    gtk.mainloop()
