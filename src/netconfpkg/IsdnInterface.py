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

import NC_functions
from NC_functions import _
import HardwareList
import NCisdnhardware
#import gnome.ui
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade
import string
import os
import providerdb
import libglade
import DialupDruid

class IsdnInterface:
    def __init__ (self, toplevel=None):
        glade_file = 'IsdnHardwareDruid.glade'

        if not os.path.isfile(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file
            
        self.xml = libglade.GladeXML(glade_file, 'druid')
        
        self.xml.signal_autoconnect(
            {
            "on_isdnCardEntry_changed" : self.on_isdnCardEntry_changed,
            "on_isdn_hardware_page_prepare" : self.on_isdn_hardware_page_prepare,
            "on_isdn_hardware_page_next" : self.on_isdn_hardware_page_next,
            "on_isdn_hardware_page_back" : self.on_isdn_hardware_page_back
            })
        
        self.toplevel = toplevel
        self.hardwarelist = HardwareList.getHardwareList()
        self.hw = None
        self.druids = []

        druid = self.xml.get_widget ('druid')
        for I in druid.children():
            druid.remove(I)
            self.druids.append(I)
            
        self.setup()

    def get_project_name(self):
        return _('ISDN connection')

    def get_project_description(self):
        return _('Create a new ISDN connection.  The ISDN interface is used primarily for connecting to an ISP over a ISDN.  This is a really lame description that should be fixed up later')

    def get_druids(self):
        Type = 'ISDN'
        dialup = DialupDruid.DialupDruid(self.toplevel, Type)
        for self.hw in self.hardwarelist:
            if self.hw.Type == Type: return dialup.get_druids()

        id = self.hardwarelist.addHardware()
        self.hw = self.hardwarelist[id]
        self.hw.Type = Type
        self.hw.createCard()
        self.hw.Name = "ISDN Card 0"
        
        return self.druids[0:] + dialup.get_druids()
            
    def on_isdn_hardware_page_prepare(self, druid_page, druid):
        pass
    
    def on_isdn_hardware_page_next(self, druid_page, druid):
        self.dehydrate()

    def on_isdn_hardware_page_back(self, druid_page, druid):
        self.hardwarelist.rollback()

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

    def setup(self):
        cardlist = NCisdnhardware.card.keys()
        cardlist.sort()
        self.xml.get_widget("isdnCardComboBox").set_popdown_strings(cardlist)

    def dehydrate(self):
        isdncard = NCisdnhardware.ConfISDN()
        isdncard.get_resource(self.xml.get_widget('isdnCardEntry').get_text())

        self.hw.Description = isdncard.Description
        self.hw.Card.ModuleName = isdncard.ModuleName
        self.hw.Card.Type = isdncard.Type

        if self.xml.get_widget("euroIsdnButton").get_active():
            self.hw.Card.ChannelProtocol = "2"
        else:
            self.hw.Card.ChannelProtocol = "1"
 
        if not self.xml.get_widget('irqSpinButton')["sensitive"]:
            self.hw.Card.IRQ = isdncard.IRQ
        else:
            self.hw.Card.IRQ = str(self.xml.get_widget('irqSpinButton').get_value_as_int())
 
        if not self.xml.get_widget('memEntry')["sensitive"]:
            self.hw.Card.Mem = isdncard.Mem
        else:
            self.hw.Card.Mem = self.xml.get_widget('memEntry').get_text()
 
        if not self.xml.get_widget('ioEntry')["sensitive"]:
            self.hw.Card.IoPort = isdncard.IoPort
        else:
            self.hw.Card.IoPort = self.xml.get_widget('ioEntry').get_text()
 
        if not self.xml.get_widget('io1Entry')["sensitive"]:
            self.hw.Card.IoPort1 = isdncard.IoPort1
        else:
            self.hw.Card.IoPort1 = self.xml.get_widget('io1Entry').get_text()
 
        if not self.xml.get_widget('io2Entry')["sensitive"]:
            self.hw.Card.IoPort2 = isdncard.IoPort2
        else:
            self.hw.Card.IoPort2 = self.xml.get_widget('io2Entry').get_text()

        
