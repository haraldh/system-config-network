# -*- coding: utf-8 -*-
## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>
## Copyright (C) 2001, 2002 Trond Eivind Glomsrød <teg@redhat.com>


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
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg import *
import gtk
from gtk import TRUE
from gtk import FALSE
import gtk.glade
import string
import os
import providerdb
import gtk.glade
import DialupDruid

class IsdnInterface:
    def __init__ (self, toplevel=None, do_save = 1, druid = None):
        self.toplevel = toplevel
        self.hardwarelist = NCHardwareList.getHardwareList()
        self.hw = None
        self.druids = []
        self.xml = None
        self.do_save = do_save

    def init_gui(self):
        if self.xml:
            return true

	if request_rpms(["isdn4k-utils"]):
            return false
 
        glade_file = 'IsdnHardwareDruid.glade'
        if not os.path.isfile(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file
            
        self.xml = gtk.glade.XML(glade_file, 'druid', GUI_functions.PROGNAME)
        
        xml_signal_autoconnect(self.xml,
            {
            "on_isdnCardEntry_changed" : self.on_isdnCardEntry_changed,
            "on_isdn_hardware_page_prepare" : self.on_isdn_hardware_page_prepare,
            "on_isdn_hardware_page_next" : self.on_isdn_hardware_page_next,
            "on_isdn_hardware_page_back" : self.on_isdn_hardware_page_back,
            'on_druid_cancel' : self.on_cancel_interface,
            })
        

        druid = self.xml.get_widget ('druid')
        for I in druid.get_children():
            druid.remove(I)
            self.druids.append(I)
            
        self.setup()

        return true
        
    def on_cancel_interface(self, *args):
        self.hardwarelist.rollback()
        devicelist = NCDeviceList.getDeviceList()
        devicelist.rollback()
        self.toplevel.destroy()
        gtk.main_quit()

    def get_project_name(self):
        return _('ISDN connection')

    def get_type(self):
        return ISDN

    def get_project_description(self):
        return _("Create a new ISDN connection. This is a connection "
                 "that uses an Integrated Services Digital Network line "
                 "to dial into to your Internet Service Provider. "
                 "This type of technology requires a special phone line "
                 "to be installed by your telephone company. "
                 "It also requires a device known as a Terminal Adapter(TA) "
                 "to terminate the ISDN connection from your ISP. "
                 "This type of connection is popular in Europe and several "
                 "other technologically advanced regions.  It is available "
                 "but uncommon in the USA.  Speeds range from 64kbps to "
                 "128kbps.")

    def get_druids(self):
        if not self.init_gui():
            return []
        
        Type = ISDN
        dialup = DialupDruid.DialupDruid(self.toplevel, Type,
                                         do_save = self.do_save)
        for hw in self.hardwarelist:
            if hw.Type == Type: return dialup.get_druids()

        self.hydrate()
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
            self.xml.get_widget("irqSpinButton").set_value(int(card.IRQ))
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

    def hydrate(self):
        has_card = FALSE
        id = self.hardwarelist.addHardware(ISDN)
        self.hw = self.hardwarelist[id]
        self.hw.Type = 'ISDN'
        self.hw.createCard()
        self.hw.Name = "ISDN Card 0"
        conf = NCisdnhardware.ConfISDN()
        new_card = conf.detect()
        cardname = ''
        if new_card:
            has_card = TRUE
            cardname = new_card.keys()[0]
            conf.get_resource(cardname)
            self.hw.Card.ChannelProtocol = '2'
            self.hw.Card.IRQ = conf.IRQ
            self.hw.Card.Mem = conf.Mem
            self.hw.Card.IoPort = conf.IoPort
            self.hw.Card.IoPort1 = conf.IoPort1
            self.hw.Card.IoPort2 = conf.IoPort2
            
        if has_card:
                if self.hw.Card.ChannelProtocol == '2':
                    self.xml.get_widget("euroIsdnButton").set_active(TRUE)
                else:
                    self.xml.get_widget("1tr6Button").set_active(TRUE)

                self.xml.get_widget("isdnCardEntry").set_text(cardname)
                
                if self.hw.Card.IRQ:
                    self.xml.get_widget("irqSpinButton").set_sensitive(TRUE)
                    self.xml.get_widget("irqSpinButton").set_value(string.atoi(self.hw.Card.IRQ))
                else:
                    self.xml.get_widget("irqSpinButton").set_sensitive(FALSE)

                if self.hw.Card.Mem:
                    self.xml.get_widget("memEntry").set_sensitive(TRUE)
                    self.xml.get_widget("memEntry").set_text(self.hw.Card.Mem)
                else:
                    self.xml.get_widget("memEntry").set_sensitive(FALSE)

                if self.hw.Card.IoPort:
                    self.xml.get_widget("ioEntry").set_sensitive(TRUE)
                    self.xml.get_widget("ioEntry").set_text(self.hw.Card.IoPort)
                else:
                    self.xml.get_widget("ioEntry").set_sensitive(FALSE)

                if self.hw.Card.IoPort1:
                    self.xml.get_widget("io1Entry").set_sensitive(TRUE)
                    self.xml.get_widget("io1Entry").set_text(self.hw.Card.IoPort1)
                else:
                    self.xml.get_widget("io1Entry").set_sensitive(FALSE)

                if self.hw.Card.IoPort2:
                    self.xml.get_widget("io2Entry").set_sensitive(TRUE)
                    self.xml.get_widget("io2Entry").set_text(self.hw.Card.IoPort2)
                else:
                    self.xml.get_widget("io2Entry").set_sensitive(FALSE)

    def dehydrate(self):
        isdncard = NCisdnhardware.ConfISDN()
        isdncard.get_resource(self.xml.get_widget('isdnCardEntry').get_text())

        self.hw.Description = isdncard.Description
        self.hw.Card.ModuleName = isdncard.ModuleName
        self.hw.Card.Type = isdncard.Type
        self.hw.Card.Firmware = isdncard.Firmware
        
        if self.xml.get_widget("euroIsdnButton").get_active():
            self.hw.Card.ChannelProtocol = "2"
        else:
            self.hw.Card.ChannelProtocol = "1"
 
        if not self.xml.get_widget('irqSpinButton').get_property("sensitive"):
            self.hw.Card.IRQ = isdncard.IRQ
        else:
            self.hw.Card.IRQ = str(self.xml.get_widget('irqSpinButton').get_value_as_int())
 
        if not self.xml.get_widget('memEntry').get_property("sensitive"):
            self.hw.Card.Mem = isdncard.Mem
        else:
            self.hw.Card.Mem = self.xml.get_widget('memEntry').get_text()
 
        if not self.xml.get_widget('ioEntry').get_property("sensitive"):
            self.hw.Card.IoPort = isdncard.IoPort
        else:
            self.hw.Card.IoPort = self.xml.get_widget('ioEntry').get_text()
 
        if not self.xml.get_widget('io1Entry').get_property("sensitive"):
            self.hw.Card.IoPort1 = isdncard.IoPort1
        else:
            self.hw.Card.IoPort1 = self.xml.get_widget('io1Entry').get_text()
 
        if not self.xml.get_widget('io2Entry').get_property("sensitive"):
            self.hw.Card.IoPort2 = isdncard.IoPort2
        else:
            self.hw.Card.IoPort2 = self.xml.get_widget('io2Entry').get_text()

NCDevIsdn.setDevIsdnWizard(IsdnInterface)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2005/03/03 17:25:26 $"
__version__ = "$Revision: 1.21 $"
