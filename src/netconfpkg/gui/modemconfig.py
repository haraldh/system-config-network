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
import types
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

from netconfpkg import NCHardwareList
from netconfpkg.gui import GUI_functions
from netconfpkg.NC_functions import _
from netconfpkg.NC_functions import modemDeviceList
from netconfpkg.NC_functions import modemFlowControls
from netconfpkg.gui.GUI_functions import load_icon
from gtk import TRUE
from gtk import FALSE

class modemDialog:
    def __init__(self, device):
        glade_file = "modemconfig.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain=GUI_functions.PROGNAME)

        self.xml.signal_autoconnect(
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        load_icon("network.xpm", self.dialog)
        self.dialog.set_close(TRUE)
        self.hw = device

        self.setup()
        self.hydrate()

        
    def on_Dialog_delete_event(self, *args):
        pass
        
    def on_okButton_clicked(self, button):
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass

    def setup(self):
        self.xml.get_widget("modemDeviceEntryCombo").set_popdown_strings(modemDeviceList)
        flowcontrols = []
        for i in modemFlowControls.keys():
            flowcontrols.append(modemFlowControls[i])
        self.xml.get_widget("flowControlCombo").set_popdown_strings(flowcontrols)        

    def hydrate(self):
        pass

    def hydrate(self):
        hardwarelist = NCHardwareList.getHardwareList()

        if self.hw.Modem.DeviceName:
            self.xml.get_widget('modemDeviceEntry').set_text(self.hw.Modem.DeviceName)
        if self.hw.Modem.BaudRate:
            self.xml.get_widget('baurateEntry').set_text(str(self.hw.Modem.BaudRate))
        if self.hw.Modem.FlowControl and modemFlowControls.has_key(self.hw.Modem.FlowControl):
            self.xml.get_widget('flowControlEntry').set_text(modemFlowControls[self.hw.Modem.FlowControl])
        if self.hw.Modem.ModemVolume:
            self.xml.get_widget('volumeMenu').set_history(int(self.hw.Modem.ModemVolume))
        if self.hw.Modem.DialCommand:
            self.xml.get_widget('toneDialingCB').set_active(self.hw.Modem.DialCommand == 'ATDT')

    def dehydrate(self):
        hardwarelist = NCHardwareList.getHardwareList()

        modem_list = []
        if not self.hw.Name:
            for i in hardwarelist:
                if i.Type == "Modem":
                    modem_list.append(i.Name)
            if modem_list:
                for i in xrange(100):
                    if modem_list.count("Modem"+str(i)) == 0:
                        self.hw.Name = "Modem" + str(i)
                        break
            else:
                self.hw.Name = "Modem0"
            
        self.hw.Modem.DeviceName = self.xml.get_widget("modemDeviceEntry").get_text()
        if os.path.dirname(hw.Modem.DeviceName) != '/dev':
            self.hw.Modem.DeviceName = '/dev/' + os.path.basename(hw.Modem.DeviceName)
        self.hw.Modem.BaudRate = string.atoi(self.xml.get_widget("baurateEntry").get_text())

        flow = self.xml.get_widget("flowControlEntry").get_text()
        for i in modemFlowControls.keys():
            if modemFlowControls[i] == flow:
                self.hw.Modem.FlowControl = i
            
        Item = self.xml.get_widget("volumeMenu")["label"]
        if Item == _("Off"):
            self.hw.Modem.ModemVolume = 0
        elif Item == _("Low"):
            self.hw.Modem.ModemVolume = 1
        elif Item == _("Medium"):
            self.hw.Modem.ModemVolume = 2
        elif Item == _("High"):
            self.hw.Modem.ModemVolume = 3
        elif Item == _("Very High"):
            self.hw.Modem.ModemVolume = 4
        else:
            self.hw.Modem.ModemVolume = 0
            
        if self.xml.get_widget("toneDialingCB")["active"]:
            self.hw.Modem.DialCommand = "ATDT"
        else:
            self.hw.Modem.DialCommand = "ATDP"

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    dialog = modemDialog()
    dialog.run()
    gtk.mainloop()

