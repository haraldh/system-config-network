# Copyright (C) 2001-2005 Red Hat, Inc.
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

from netconfpkg.gui.GUI_functions import *
from netconfpkg import *
import gtk
from gtk import TRUE
from gtk import FALSE
import gtk.glade
import string
import os
from rhpl import Conf
from ethernethardware import ethernetHardwareDialog
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg import NCHardwareList

class ethernetHardware:
    def __init__ (self, toplevel=None):

        glade_file = "EthernetHardwareDruid.glade"
 
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
        self.has_ethernet = TRUE
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
            if self.hw.Type == ETHERNET: return

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
        else:
            hwlist = NCHardwareList.getHardwareList()
            nextDevice = NCHardwareList.getNextDev('eth')
            self.xml.get_widget('ethernetDeviceEntry').set_text(nextDevice)

    def setup(self):
        list = []
        modInfo = NCHardwareList.getModInfo()
        for i in modInfo.keys():
            if modInfo[i]['type'] == "eth":
                if modInfo[i].has_key('description') and \
                       len(modInfo[i]['description']):
                    list.append(modInfo[i]['description'])
                else:
                    list.append(i)
        list.sort()
        self.xml.get_widget("adapterComboBox").set_popdown_strings(list)

#          hwlist = NCHardwareList.getHardwareList()
#          (hwcurr, hwdesc) = create_ethernet_combo(hwlist, None)
        
#          if len(hwdesc):
#              self.xml.get_widget("adapterComboBox").set_popdown_strings(hwdesc)

    def dehydrate(self):
        if not self.has_ethernet:
            id = self.hardwarelist.addHardware(ETHERNET)
            self.hw = self.hardwarelist[id]
        self.hw.Type = 'Ethernet'
        self.hw.createCard()
        self.hw.Name = self.xml.get_widget('ethernetDeviceEntry').get_text()
        self.hw.Description = self.xml.get_widget('adapterEntry').get_text()
        if self.xml.get_widget('irqEntry').get_text() == 'Unknown' or \
           self.xml.get_widget('irqEntry').get_text() == _('Unknown'):
            self.hw.Card.IRQ = None
        else: self.hw.Card.IRQ = self.xml.get_widget('irqEntry').get_text()
        self.hw.Card.Mem = self.xml.get_widget('memEntry').get_text()
        self.hw.Card.IoPort = self.xml.get_widget('ioEntry').get_text()
        self.hw.Card.IoPort1 = self.xml.get_widget('io1Entry').get_text()
        self.hw.Card.IoPort2 = self.xml.get_widget('io2Entry').get_text()
        self.hw.Card.DMA0 = self.xml.get_widget('dma0Entry').get_text()
        self.hw.Card.DMA1 = self.xml.get_widget('dma1Entry').get_text()
        modInfo = NCHardwareList.getModInfo()
        self.hw.Card.ModuleName = 'Unknown'
        for i in modInfo.keys():
            if (modInfo[i].has_key('description') and \
                modInfo[i]['description'] == self.hw.Description) or \
                (self.hw.Description == i):
                self.hw.Card.ModuleName = i         
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2005/03/03 17:25:26 $"
__version__ = "$Revision: 1.28 $"
