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
import NC_functions
from NC_functions import _
from NC_functions import modemDeviceList
from gtk import TRUE
from gtk import FALSE

class modemDialog:
    def __init__(self):
        glade_file = "modemconfig.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = NC_functions.NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain=NC_functions.PROGNAME)

        self.xml.signal_autoconnect(
            {
            "on_volumeCB_toggled" : self.on_volumeCB_toggled,
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.edit = FALSE
        self.Name = None
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

    def on_volumeCB_toggled(self, check):
        scale = self.xml.get_widget("volumeMenu")
        scale.set_sensitive(check["active"])
        scale.grab_focus()

    def setup(self):
        self.xml.get_widget("modemDeviceEntryComBo").set_popdown_strings(modemDeviceList)

    def hydrate(self):
        pass

    def dehydrate(self):
        hardwarelist = HardwareList.getHardwareList()

        modem_list = []
        if not self.edit:
            for i in hardwarelist:
                if i.Type == "Modem":
                    modem_list.append(i.Name)
            if modem_list:
                for i in xrange(100):
                    if modem_list.count("Modem"+str(i)) == 0:
                        self.Name = "Modem" + str(i)
                        break
            else:
                self.Name = "Modem0"
            
            id = hardwarelist.addHardware()
            hw = hardwarelist[id]
            hw.Type = "Modem"
            hw.Name = self.Name
            hw.Description = "Generic Modem"
            hw.createModem()
        else:
            for hw in hardwarelist:
                if hw.Name == self.Name:
                    break

        hw.Modem.DeviceName = self.xml.get_widget("modemDeviceEntry").get_text()
        hw.Modem.BaudRate = string.atoi(self.xml.get_widget("baurateEntry").get_text())
        hw.Modem.FlowControl = self.xml.get_widget("flowControlEntry").get_text()
        if self.xml.get_widget("volumeCB")["active"]:
            Item = self.xml.get_widget("volumeMenu")["label"]
            if Item == _("Low"):
                hw.Modem.ModemVolume = 1
            elif Item == _("Medium"):
                hw.Modem.ModemVolume = 2
            elif Item == _("High"):
                hw.Modem.ModemVolume = 3
            elif Item == _("Very High"):
                hw.Modem.ModemVolume = 4
        else:
            hw.Modem.ModemVolume = 0
            
        if self.xml.get_widget("toneDialingCB")["active"]:
            hw.Modem.DialCommand = "ATDT"
        else:
            hw.Modem.DialCommand = "ATDP"

class addmodemDialog(modemDialog):
    def __init__(self):
        modemDialog.__init__(self)
        self.edit = FALSE

class editmodemDialog(modemDialog):
    def __init__(self, Dev):
        self.Dev = Dev
        modemDialog.__init__(self)
        self.edit = TRUE
        self.Name = self.Dev
        
    def hydrate(self):
        hardwarelist = HardwareList.getHardwareList()

        for hw in hardwarelist:
            if hw.Name == self.Dev:
                self.xml.get_widget('modemDeviceEntry').set_text(hw.Modem.DeviceName)
                self.xml.get_widget('baurateEntry').set_text(str(hw.Modem.BaudRate))
                if hw.Modem.FlowControl:
                    self.xml.get_widget('flowControlEntry').set_text(hw.Modem.FlowControl)
                    
                self.xml.get_widget('volumeCB').set_active(hw.Modem.ModemVolume != 0)
                self.xml.get_widget('volumeMenu').set_sensitive(hw.Modem.ModemVolume != 0)

                if hw.Modem.ModemVolume > 0:
                    self.xml.get_widget('volumeMenu').set_history(int(hw.Modem.ModemVolume)-1)

                self.xml.get_widget('toneDialingCB').set_active(hw.Modem.DialCommand == 'ATDT')


# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    dialog = modemDialog()
    dialog.run()
    gtk.mainloop()

