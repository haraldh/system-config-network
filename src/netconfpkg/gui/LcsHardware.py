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
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import gtk
import gtk.glade
import signal
import os
import string
import re
from rhpl.executil import *
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg import *
from netconfpkg import NCHWLcs
from netconfpkg import NCHardwareList
from netconfpkg.Control import NetworkDevice

class lcsHardwareDialog:
    def __init__(self, hw):
        self.hw = hw

        glade_file = "LcsHardware.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_adapterEntry_changed" : self.on_adapterEntry_changed
            })

        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        load_icon("network.xpm", self.dialog)
        
        self.setup()
        self.hydrate()

    def on_Dialog_delete_event(self, *args):
        pass

    def on_okButton_clicked(self, button):
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass
    
    def on_adapterEntry_changed(self, entry):
        pass

    def hydrate(self):
        if self.hw.Name:
            self.xml.get_widget('ethernetDeviceEntry').set_text(self.hw.Name)
            if self.hw.Card.IoPort:
                self.xml.get_widget('ioEntry').set_text(self.hw.Card.IoPort)
            if self.hw.Card.IoPort1:
                self.xml.get_widget('io1Entry').set_text(self.hw.Card.IoPort1)
            if self.hw.Card.IoPort2:
                self.xml.get_widget('io2Entry').set_text(self.hw.Card.IoPort2)
            if self.hw.Card.Options:
                self.xml.get_widget('optionsEntry').set_text(self.hw.Card.Options)
            if self.hw.MacAddress:
                self.xml.get_widget('macEntry').set_text(self.hw.MacAddress)
        else:
            hwlist = NCHardwareList.getHardwareList()
            nextDevice = NCHardwareList.getNextDev('eth')
            self.xml.get_widget('ethernetDeviceEntry').set_text(nextDevice)
            
    def setup(self):
        activedevicelist = NetworkDevice().get()
        if self.hw.Name in activedevicelist:
            ret = generic_yesno_dialog (_("Do you want to deactive interface %s first?\n"
                                          "Otherwise saving changes may have unwanted side effects." % self.hw.Name),
                                        self.dialog)
            if ret == RESPONSE_YES:
                devicelist = getDeviceList()
                for dev in devicelist:
                    if self.hw.Name == dev.Device:
                        dev.deactivate()

    def dehydrate(self):
        self.hw.Name = self.xml.get_widget('ethernetDeviceEntry').get_text()
        if not self.hw.Type:
            self.hw.Type = LCS
        self.hw.createCard()
        self.hw.Card.IoPort = self.xml.get_widget('ioEntry').get_text()
        self.hw.Card.IoPort1 = self.xml.get_widget('io1Entry').get_text()
        self.hw.Card.IoPort2 = self.xml.get_widget('io2Entry').get_text()
        self.hw.Card.Options = self.xml.get_widget('optionsEntry').get_text()
        self.hw.Card.ModuleName = "lcs"
        self.hw.Description = "lcs %s,%s,%s" % (self.hw.Card.IoPort, self.hw.Card.IoPort1, self.hw.Card.IoPort2)
        self.hw.MacAddress = self.xml.get_widget('macEntry').get_text()

NCHWLcs.setHwLcsDialog(lcsHardwareDialog)
__author__ = "Harald Hoyer <harald@redhat.com>"
