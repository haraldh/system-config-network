## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
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

from dialupconfig import *
from ethernetconfig import ethernetConfigDialog
from dslconfig import dslConfigDialog
from netconfpkg.gui.GUI_functions import *
from netconfpkg.gui.GUI_functions import load_icon
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg import NCHardwareList
from gtk import TRUE
from gtk import FALSE


class deviceTypeDialog:
    def __init__(self, device):
        self.device = device
        glade_file = "devicetype.glade"

        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=PROGNAME)
        xml_signal_autoconnect(self.xml,
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            })

        self.dialog = self.xml.get_widget("Dialog")
        load_icon("network.xpm", self.dialog)

        devicetypes=deviceTypes[:]
        devicetypes.remove(LO)

        hardwarelist = NCHardwareList.getHardwareList()
        machine = os.uname()[4]
        ethernetFound = FALSE
        modemFound = FALSE
        isdnFound = FALSE
        tokenringFound = FALSE
        adslFound = FALSE
        cipeFound = FALSE
        wirelessFound = FALSE
        for hw in hardwarelist:
            if hw.Type == MODEM: modemFound = TRUE
            elif hw.Type == ISDN: isdnFound = TRUE
            elif hw.Type == ETHERNET:
                ethernetFound = TRUE
                adslFound = TRUE
                cipeFound = TRUE
                wirelessFound = TRUE
            elif hw.Type == TOKENRING: tokenringFound = TRUE
        if machine == 's390' or machine == 's390x':
            modemFound = FALSE
            isdnFound = FALSE
            adslFound = FALSE
            wirelessFound = FALSE
        else:
            devicetypes.remove(CTC)
            devicetypes.remove(IUCV)
        if not modemFound: devicetypes.remove(MODEM)
        if not isdnFound: devicetypes.remove(ISDN)
        if not ethernetFound: devicetypes.remove(ETHERNET)
        if not adslFound: devicetypes.remove(DSL)
        if not cipeFound: devicetypes.remove(CIPE)
        if not tokenringFound: devicetypes.remove(TOKENRING)
        if not wirelessFound: devicetypes.remove(WIRELESS)
        
        omenu = self.xml.get_widget('deviceTypeOption')
        omenu.remove_menu ()
        menu = gtk.Menu ()
        for device_name in devicetypes:
            menu_item = gtk.MenuItem (device_name)
            menu_item.set_data ("device", device_name)
            menu_item.show ()
            menu.append (menu_item)
        menu.show ()
        omenu.set_menu (menu)
        omenu.grab_focus ()
        self.hydrate()
        

    def hydrate(self):
        pass
    
    def dehydrate(self):
        omenu = self.xml.get_widget('deviceTypeOption')
        item = omenu.get_menu ().get_active ()
        self.device.Type = item.get_data ("device")
        
    def on_okButton_clicked(self, button):
        self.dehydrate()
    
    def on_cancelButton_clicked(self, button):
        self.device.rollback()
    

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = basicDialog()
    gtk.main()

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2005/03/03 17:25:26 $"
__version__ = "$Revision: 1.15 $"
