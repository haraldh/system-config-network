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

import HardwareList
import NCisdnhardware
import NC_functions

from gtk import TRUE
from gtk import FALSE

##
## I18N
##
gettext.bindtextdomain(NC_functions.PROGNAME, "/usr/share/locale")
gettext.textdomain(NC_functions.PROGNAME)
_=gettext.gettext

class isdnHardwareDialog:
    def __init__(self):
        glade_file = "isdnhardware.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = NC_functions.NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain=NC_functions.PROGNAME)

        self.xml.signal_autoconnect(
            {
            "on_isdnCardEntry_changed" : self.on_isdnCardEntry_changed,
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.edit = FALSE
        self.dialog = self.xml.get_widget("Dialog")
        NC_functions.load_icon("network.xpm", self.dialog)
        self.dialog.set_close(TRUE)
        self.setup()
        self.hydrate()

    def on_Dialog_delete_event(self, *args):
        pass

    def on_okButton_clicked(self, button):
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass

    def on_isdnCardEntry_changed(self, entry):
        cardname = entry.get_text()
        card = NCisdnhardware.ConfISDN()
        card.get_resource(cardname)
        
        if card.IRQ:
            self.xml.get_widget("irqSpinButton").set_sensitive(TRUE)
            self.xml.get_widget("irqSpinButton").set_value(string.atoi(card.IRQ))
        else:
            self.xml.get_widget("irqSpinButton").set_sensitive(FALSE)

        if card.Mem:
            self.xml.get_widget("memEntry").set_sensitive(TRUE)
            self.xml.get_widget("memEntry").set_text(card.Mem)
        else:
            self.xml.get_widget("memEntry").set_sensitive(FALSE)

        if card.IoPort:
            self.xml.get_widget("ioEntry").set_sensitive(TRUE)
            self.xml.get_widget("ioEntry").set_text(card.IoPort)
        else:
            self.xml.get_widget("ioEntry").set_sensitive(FALSE)

        if card.IoPort1:
            self.xml.get_widget("io1Entry").set_sensitive(TRUE)
            self.xml.get_widget("io1Entry").set_text(card.IoPort1)
        else:
            self.xml.get_widget("io1Entry").set_sensitive(FALSE)

        if card.IoPort2:
            self.xml.get_widget("io2Entry").set_sensitive(TRUE)
            self.xml.get_widget("io2Entry").set_text(card.IoPort2)
        else:
            self.xml.get_widget("io2Entry").set_sensitive(FALSE)

    def hydrate(self):
        pass

    def dehydrate(self):
        hardwarelist = HardwareList.getHardwareList()
        isdncard = NCisdnhardware.ConfISDN()
        isdncard.get_resource(self.xml.get_widget('adapterEntry').get_text())

        if not self.edit:
            id = hardwarelist.addHardware()
            hw = hardwarelist[id]
            hw.Type = "ISDN"
            hw.createCard()
        else:
            for hw in hardwarelist:
                if hw.Type == "ISDN":
                    break

        hw.Name = "ISDN Card 0"
        hw.Description = isdncard.Description
        hw.Card.ModuleName = isdncard.ModuleName
        hw.Card.Type = isdncard.Type

        if self.xml.get_widget("euroIsdnButton").get_active():
            hw.Card.ChannelProtocol = "2"
        else:
            hw.Card.ChannelProtocol = "1"

        if not self.xml.get_widget('irqSpinButton')["sensitive"]:
            hw.Card.IRQ = isdncard.IRQ
        else:
            hw.Card.IRQ = str(self.xml.get_widget('irqSpinButton').get_value_as_int())

        if not self.xml.get_widget('memEntry')["sensitive"]:
            hw.Card.Mem = isdncard.Mem
        else:
            hw.Card.Mem = self.xml.get_widget('memEntry').get_text()

        if not self.xml.get_widget('ioEntry')["sensitive"]:
            hw.Card.IoPort = isdncard.IoPort
        else:
            hw.Card.IoPort = self.xml.get_widget('ioEntry').get_text()

        if not self.xml.get_widget('io1Entry')["sensitive"]:
            hw.Card.IoPort1 = isdncard.IoPort1
        else:
            hw.Card.IoPort1 = self.xml.get_widget('io1Entry').get_text()

        if not self.xml.get_widget('io2Entry')["sensitive"]:
            hw.Card.IoPort2 = isdncard.IoPort2
        else:
            hw.Card.IoPort2 = self.xml.get_widget('io2Entry').get_text()

    def setup(self):
        cardlist = NCisdnhardware.card.keys()
        cardlist.sort()
        self.xml.get_widget("isdnCardComboBox").set_popdown_strings(cardlist)


    
class addisdnHardwareDialog(isdnHardwareDialog):
    def __init__(self):
        isdnHardwareDialog.__init__(self)
        self.edit = FALSE

class editisdnHardwareDialog(isdnHardwareDialog):
    def __init__(self, cardname):
        self.cardname = cardname
        isdnHardwareDialog.__init__(self)
        self.edit = TRUE

    def hydrate(self):
        hardwarelist = HardwareList.getHardwareList()

        for hw in hardwarelist:
            if hw.Type == "ISDN":
                if hw.Card.ChannelProtocol == "2":
                    self.xml.get_widget("euroIsdnButton").set_active(TRUE)
                else:
                    self.xml.get_widget("1tr6Button").set_active(TRUE)

                self.xml.get_widget("adapterEntry").set_text(self.cardname)
                
                if hw.Card.IRQ:
                    self.xml.get_widget("irqSpinButton").set_sensitive(TRUE)
                    self.xml.get_widget("irqSpinButton").set_value(string.atoi(hw.Card.IRQ))
                else:
                    self.xml.get_widget("irqSpinButton").set_sensitive(FALSE)

                if hw.Card.Mem:
                    self.xml.get_widget("memEntry").set_sensitive(TRUE)
                    self.xml.get_widget("memEntry").set_text(hw.Card.Mem)
                else:
                    self.xml.get_widget("memEntry").set_sensitive(FALSE)

                if hw.Card.IoPort:
                    self.xml.get_widget("ioEntry").set_sensitive(TRUE)
                    self.xml.get_widget("ioEntry").set_text(hw.Card.IoPort)
                else:
                    self.xml.get_widget("ioEntry").set_sensitive(FALSE)

                if hw.Card.IoPort1:
                    self.xml.get_widget("io1Entry").set_sensitive(TRUE)
                    self.xml.get_widget("io1Entry").set_text(hw.Card.IoPort1)
                else:
                    self.xml.get_widget("io1Entry").set_sensitive(FALSE)

                if hw.Card.IoPort2:
                    self.xml.get_widget("io2Entry").set_sensitive(TRUE)
                    self.xml.get_widget("io2Entry").set_text(hw.Card.IoPort2)
                else:
                    self.xml.get_widget("io2Entry").set_sensitive(FALSE)
    

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = isdnHardwareDialog()
    gtk.mainloop()
