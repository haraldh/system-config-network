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
import string

import HardwareList

from deviceconfig import deviceConfigDialog
from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class dslConfigDialog(deviceConfigDialog):
    def __init__(self, device, xml_main = None, xml_basic = None):
        glade_file = "dslconfig.glade"
        deviceConfigDialog.__init__(self, glade_file,
                                    device, xml_main, xml_basic)
        
    def hydrate(self):
        deviceConfigDialog.hydrate(self)
        dialup = self.device.Dialup
        ecombo = self.xml.get_widget("ethernetDeviceComboBox")

        hwdesc = []
        hwcurr = None
        hardwarelist = HardwareList.getHardwareList()
        for hw in hardwarelist:
            if hw.Type == "Ethernet":
                desc = str(hw.Name) + ' (' + hw.Description + ')'
                hwdesc.append(desc)
                if dialup.EthDevice and \
                   hw.Name == dialup.EthDevice:
                    hwcurr = desc
                    
        if len(hwdesc):
            hwdesc.sort()
            ecombo.set_popdown_strings(hwdesc)

        if not hwcurr and len(hwdesc):
            hwcurr = hwdesc[0]

        widget = self.xml.get_widget("ethernetDeviceEntry")
        if dialup.EthDevice:
            widget.set_text(hwcurr)
        widget.set_position(0)
            
        if dialup.ProviderName:
            self.xml.get_widget("providerNameEntry").set_text(dialup.ProviderName)

        if dialup.Login:
            self.xml.get_widget("loginNameEntry").set_text(dialup.Login)

        if dialup.Password:
            self.xml.get_widget("passwordEntry").set_text(dialup.Password)
            
        if dialup.ServiceName:
            self.xml.get_widget("serviceNameEntry").set_text(dialup.ServiceName)

        if dialup.AcName:
            self.xml.get_widget("acNameEntry").set_text(dialup.AcName)

        self.xml.get_widget("useSyncpppCB").set_active(dialup.SyncPPP == TRUE)

    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        dialup = self.device.Dialup
        hw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        fields = string.split(hw)
        hw = fields[0]
        dialup.EthDevice = hw
        dialup.ProviderName = self.xml.get_widget("providerNameEntry").get_text()
        dialup.Login = self.xml.get_widget("loginNameEntry").get_text()
        dialup.Password = self.xml.get_widget("passwordEntry").get_text()
        dialup.ServiceName = self.xml.get_widget("serviceNameEntry").get_text()
        dialup.AcName = self.xml.get_widget("acNameEntry").get_text()
        if self.xml.get_widget("useSyncpppCB").get_active():
            dialup.SyncPPP = TRUE
        else: dialup.SyncPPP = FALSE
        
        if not self.device.Device:
            self.device.Device="dsl"
        
    
# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    dslConfigDialog()
    gtk.mainloop()
