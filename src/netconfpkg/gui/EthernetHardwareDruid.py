# Copyright (C) 2001 Red Hat, Inc.
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

from netconfpkg.gui.GUI_functions import *
from netconfpkg.NC_functions import _
from netconfpkg import NCHardwareList
#import gnome.ui
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade
import string
import os
from netconfpkg import Conf
from ethernethardware import ethernetHardwareDialog

class ethernetHardware:
    def __init__ (self, toplevel=None):

        glade_file = "EthernetHardwareDruid.glade"
 
        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file
 
        self.xml = libglade.GladeXML(glade_file, 'druid')
        self.xml.signal_autoconnect(
            {
            "on_adapterEntry_changed" : self.on_adapterEntry_changed,
            "on_hardware_page_prepare" : self.on_hardware_page_prepare,
            "on_hardware_page_next" : self.on_hardware_page_next,
            "on_hardware_page_back" : self.on_hardware_page_back
            })

        self.toplevel = toplevel
        self.hardwarelist = NCHardwareList.getHardwareList()
        self.hw = None
        self.has_ethernet = TRUE
        self.druids = []
 
        druid = self.xml.get_widget('druid')
        for I in druid.children():
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
            if self.hw.Type == 'Ethernet': return

        self.has_ethernet = FALSE
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

#          hwlist = NCHardwareList.getHardwareList()
#          (hwcurr, hwdesc) = create_ethernet_combo(hwlist, None)
        
#          if len(hwdesc):
#              self.xml.get_widget("adapterComboBox").set_popdown_strings(hwdesc)

    def dehydrate(self):
        if not self.has_ethernet:
            id = self.hardwarelist.addHardware()
            self.hw = self.hardwarelist[id]
        self.hw.Type = 'Ethernet'
        self.hw.createCard()
        self.hw.Name = self.xml.get_widget('ethernetDeviceEntry').get_text()
        self.hw.Description = self.xml.get_widget('adapterEntry').get_text()
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

