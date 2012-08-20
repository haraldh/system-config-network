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

from netconfpkg.gui.GUI_functions import *
from netconfpkg import *
from netconfpkg.plugins import NCHWLcs
import gtk
import gtk.glade
import string
import os
from netconfpkg.conf import Conf

class LcsHardware:
    def __init__ (self, toplevel=None):

        glade_file = "LcsHardwareDruid.glade"
 
        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file
 
        self.xml = gtk.glade.XML(glade_file, 'druid',
                                     domain=PROGNAME)
        xml_signal_autoconnect(self.xml,
            {
            "on_adapterEntry_changed" : self.on_adapterEntry_changed,
            "on_hardware_page_prepare" : self.on_hardware_page_prepare,
            "on_hardware_page_next" : self.on_hardware_page_next,
            "on_hardware_page_back" : self.on_hardware_page_back
            })

        self.toplevel = toplevel
        self.hardwarelist = NCHardwareList.getHardwareList()
        self.hw = None
        self.has_ethernet = True
        self.druids = []
 
        druid = self.xml.get_widget('druid')
        for I in druid.get_children():
            druid.remove(I)
            self.druids.append(I)
            
        self.setup()
        self.hydrate()
        
    def get_project_name(self):
        pass

    def get_project_description(self):
        pass
    
    def get_druids(self):
        for self.hw in self.hardwarelist:
            if self.hw.Type == LCS: return

        self.has_ethernet = False
        return self.druids[0:]

    def on_hardware_page_prepare(self, druid_page, druid):
        pass
    
    def on_hardware_page_next(self, druid_page, druid):
        self.dehydrate()

    def on_hardware_page_back(self, druid_page, druid):
        self.hardwarelist.rollback()

    def on_adapterEntry_changed(self, entry):
        pass
    
    def hydrate(self):
        if self.hw and self.hw.Name:
            self.xml.get_widget('ethernetDeviceEntry').set_text(self.hw.Name)
            if self.hw.Card:
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
#          hwlist = NCHardwareList.getHardwareList()
#          (hwcurr, hwdesc) = create_ethernet_combo(hwlist, None)
        
#          if len(hwdesc):
#              self.xml.get_widget("adapterComboBox").set_popdown_strings(hwdesc)
        pass

    def dehydrate(self):
        if not self.has_ethernet:
            id = self.hardwarelist.addHardware(LCS)
            self.hw = self.hardwarelist[id]
        self.hw.Type = LCS
        self.hw.createCard()
        self.hw.Name = self.xml.get_widget('ethernetDeviceEntry').get_text()
        self.hw.Card.IoPort = self.xml.get_widget('ioEntry').get_text()
        self.hw.Card.IoPort1 = self.xml.get_widget('io1Entry').get_text()
        self.hw.Card.IoPort2 = self.xml.get_widget('io2Entry').get_text()
        self.hw.Card.Options = self.xml.get_widget('optionsEntry').get_text()
        self.hw.Card.ModuleName = 'lcs'
        self.hw.Description = "lcs %s,%s,%s" % (self.hw.Card.IoPort, self.hw.Card.IoPort1, self.hw.Card.IoPort2)
        self.hw.MacAddress = self.xml.get_widget('macEntry').get_text()


NCHWLcs.setHwLcsWizard(LcsHardware)

__author__ = "Harald Hoyer <harald@redhat.com>"
