## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
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
import gtk
import gtk.glade
import signal
import os

import string
from rhpl import Conf
from netconfpkg.gui import GUI_functions
from netconfpkg import *
from netconfpkg.gui.HardwareDialog import HardwareDialog
from gtk import TRUE
from gtk import FALSE

class tokenringHardwareDialog(HardwareDialog):
    def __init__(self, hw):
        HardwareDialog.__init__(self, hw,
                                "tokenringhardware.glade",
                                {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_adapterEntry_changed" : self.on_adapterEntry_changed
            })
                                
        self.button = 0

    def on_okButton_clicked(self, button):
        HardwareDialog.on_okButton_clicked(self, button)
        cmd = [ '/sbin/modprobe ', self.hw.Card.ModuleName ]
        if self.hw.Card.IRQ:
            cmd.append(' irq='+self.hw.Card.IRQ)
        if self.hw.Card.IoPort:
            cmd.append(' io='+self.hw.Card.IoPort)
        if self.hw.Card.IoPort1:
            cmd.append(' io1='+self.hw.Card.IoPort1)
        if self.hw.Card.IoPort2:
            cmd.append(' io2='+self.hw.Card.IoPort2)
        if self.hw.Card.Mem:
            cmd.append(' mem='+self.hw.Card.Mem)
        if self.hw.Card.DMA0:
            cmd.append(' dma='+str(self.hw.Card.DMA0))
        if self.hw.Card.DMA1:
            cmd.append(' dma1='+str(self.hw.Card.DMA1))
            
        (status, output) = gtkExecWithCaptureStatus('/sbin/modprobe', cmd,
                                                    catchfd = (1, 2))
        if status != 0:
            output = _('Command failed: %s\n\nOutput:\n%s\n') % (string.join(cmd), output)
            GUI_functions.generic_longinfo_dialog(\
                _('The Token Ring card could not be initialized. '
                  'Please verify your settings and try again.'),
                output, self.dialog)
        pass

    def on_cancelButton_clicked(self, button):
        #self.button = 1
        pass

    def on_adapterEntry_changed(self, entry):
        pass

    def hydrate(self):
        HardwareDialog.hydrate(self)
        
        if self.hw.Name:
            self.xml.get_widget('tokenringDeviceEntry').set_text(self.hw.Name)
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
        HardwareDialog.setup(self)
        
        list = []
        modInfo = NCHardwareList.getModInfo()
        for i in modInfo.keys():
            if modInfo[i]['type'] == "tr" and \
                   modInfo[i].has_key('description'):
                list.append(modInfo[i]['description'])
        list.sort()
        self.xml.get_widget("adapterComboBox").set_popdown_strings(list)
        nextdev = NCHardwareList.getNextDev("tr")
        self.xml.get_widget('tokenringDeviceEntry').set_text(nextdev)

    def dehydrate(self):
        HardwareDialog.dehydrate(self)
        
        self.hw.Name = self.xml.get_widget('tokenringDeviceEntry').get_text()
        self.hw.Description = self.xml.get_widget('adapterEntry').get_text()
        self.hw.Type = 'Token Ring'
        self.hw.createCard()
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
        if not self.hw.Card.ModuleName or self.hw.Card.ModuleName == "":
            self.hw.Card.ModuleName = _('Unknown')
        for i in modInfo.keys():
            if modInfo[i].has_key('description') and \
                   modInfo[i]['description'] == self.hw.Description:
                self.hw.Card.ModuleName = i


NCHWTokenring.setHwTokenringDialog(tokenringHardwareDialog)


