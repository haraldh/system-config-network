## Copyright (C) 2001, 2002 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001, 2002 Harald Hoyer <harald@redhat.com>
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

import sys
sys.path.append("/usr/lib/rhs/python/")


import gtk

import gtk
import gtk.glade
import signal
import os
import string
import re
import commands
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon
from netconfpkg import *

from gtk import TRUE
from gtk import FALSE

class ethernetHardwareDialog:
    def __init__(self, hw):
        self.hw = hw

        glade_file = "ethernethardware.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=GUI_functions.PROGNAME)

        self.xml.signal_autoconnect(
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
        cmd = '/sbin/modprobe '+self.hw.Card.ModuleName
        if self.hw.Card.IRQ:
            cmd = cmd + ' irq='+self.hw.Card.IRQ
        if self.hw.Card.IoPort:
            cmd = cmd + ' io='+self.hw.Card.IoPort
        if self.hw.Card.IoPort1:
            cmd = cmd + ' io1='+self.hw.Card.IoPort1
        if self.hw.Card.IoPort2:
            cmd = cmd + ' io2='+self.hw.Card.IoPort2
        if self.hw.Card.Mem:
            cmd = cmd + ' mem='+self.hw.Card.Mem
        if self.hw.Card.DMA0:
            cmd = cmd + ' dma='+str(self.hw.Card.DMA0)
        if self.hw.Card.DMA1:
            cmd = cmd + ' dma1='+str(self.hw.Card.DMA1)
        (status, output) = commands.getstatusoutput(cmd)
        if status != 0:
            GUI_functions.generic_error_dialog('The Ethernet card could not be initialized. Please verify your settings and try again.', self.dialog)
        pass

    def on_cancelButton_clicked(self, button):
        pass
    
    def on_adapterEntry_changed(self, entry):
        pass

    def hydrate(self):
        if self.hw.Name:
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
                self.xml.get_widget('dma0Entry').set_text(str(self.hw.Card.DMA0))
            if self.hw.Card.DMA1:
                self.xml.get_widget('dma1Entry').set_text(str(self.hw.Card.DMA1))

    def setup(self):
        list = []
        modInfo = NCHardwareList.getModInfo()
        for i in modInfo.keys():
            if modInfo[i]['type'] == "eth":
                if modInfo[i].has_key('description') and \
                       len(modInfo[i][description]):
                    list.append(modInfo[i]['description'])
                else:
                    list.append(i)
        list.sort()
        self.xml.get_widget("adapterComboBox").set_popdown_strings(list)

    def dehydrate(self):
        self.hw.Name = self.xml.get_widget('ethernetDeviceEntry').get_text()
        self.hw.Description = self.xml.get_widget('adapterEntry').get_text()
        self.hw.Type = 'Ethernet'
        self.hw.createCard()
        if self.xml.get_widget('irqEntry').get_text() == 'Unknown' or \
           self.xml.get_widget('irqEntry').get_text() == _('Unknown'):
            self.hw.Card.IRQ = None
        else: self.hw.Card.IRQ = self.xml.get_widget('irqEntry').get_text()
        
        self.hw.Card.Mem = self.xml.get_widget('memEntry').get_text()
        self.hw.Card.IoPort = self.xml.get_widget('ioEntry').get_text()
        self.hw.Card.IoPort1 = self.xml.get_widget('io1Entry').get_text()
        self.hw.Card.IoPort2 = self.xml.get_widget('io2Entry').get_text()
        val=self.xml.get_widget('dma0Entry').get_text()
        if val:
            self.hw.Card.DMA0 = int(val)
        val=self.xml.get_widget('dma1Entry').get_text()
        if val:
            self.hw.card.DMA1 = int(val)

        modInfo = NCHardwareList.getModInfo()
        if not self.hw.Card.ModuleName or self.hw.Card.ModuleName == "":
            self.hw.Card.ModuleName = _('Unknown')
        for i in modInfo.keys():
            if modInfo[i].has_key('description') and \
                   modInfo[i]['description'] == self.hw.Description:
                self.hw.Card.ModuleName = i

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = ethernetHardwareDialog()
    gtk.mainloop()
