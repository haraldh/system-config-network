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
import re

import NCHardwareList
from NC_functions import *
from NC_functions import _
from gtk import TRUE
from gtk import FALSE


class hardwareTypeDialog:
    def __init__(self, xml = None):
        self.xml_main = xml
        glade_file = "hardwaretype.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain=PROGNAME)
        self.xml.signal_autoconnect(
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            })

        self.dialog = self.xml.get_widget("Dialog")
        load_icon("network.xpm", self.dialog)

        hardwarelist = NCHardwareList.getHardwareList()
        devicetypes = ['Ethernet', 'Modem', 'ISDN', 'Token Ring']
        for hw in hardwarelist:
            if hw.Type == 'ISDN':
                devicetypes = ['Ethernet', 'Modem', 'Token Ring']

        self.xml.get_widget('hardwareTypeCombo').set_popdown_strings(devicetypes)
        self.hydrate()

        self.dialog.set_close(TRUE)

    def hydrate(self):
        pass
    
    def dehydrate(self):
        self.type = self.xml.get_widget('hardwareTypeEntry').get_text()

    def on_okButton_clicked(self, button):
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass


# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = basicDialog()
    gtk.mainloop()

