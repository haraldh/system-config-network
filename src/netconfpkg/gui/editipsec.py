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

import gtk

import gtk
import gtk.glade
import signal
import os

import string
import re
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from rhpl.executil import *

from gtk import TRUE
from gtk import FALSE

class editIPsecDruid:
    def __init__(self, ipsec=None):
        self.ipsec = ipsec

        glade_file = "editipsec.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None,
                                 domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml, {
            "on_ipsecDruidConnectionTypePage_prepare" :
            self.on_ipsecDruidConnectionTypePage_prepare,
            "on_ipsecDruidConnectionTypePage_next" :
            self.on_ipsecDruidConnectionTypePage_next,
            "on_ipsecDruidEncryptionModePage_prepare" :
            self.on_ipsecDruidEncryptionModePage_prepare,
            "on_ipsecDruidEncryptionModePage_next" :
            self.on_ipsecDruidEncryptionModePage_next,
            "on_ipsecDruidLocalNetworkPage_prepare" :
            self.on_ipsecDruidLocalNetworkPage_prepare,
            "on_ipsecDruidRemoteNetworkPage_prepare" :
            self.on_ipsecDruidRemoteNetworkPage_prepare,
            "on_ipsecDruidKeysPage_prepare" :
            self.on_ipsecDruidKeysPage_prepare,
            "on_ipsecDruidFinishPage_prepare" :
            self.on_ipsecDruidFinishPage_prepare,
            "on_ipsecDruidFinishPage_finish" :
            self.on_ipsecDruidFinishPage_finish,
            "on_generateAHKeyButton_clicked" :
            self.on_generateAHKeyButton_clicked,
            "on_generateESPKeyButton_clicked" :
            self.on_generateESPKeyButton_clicked,
            "on_ipsecDruid_cancel" : self.on_ipsecDruid_cancel,
            })
        
        self.druid = self.xml.get_widget("Druid")
        self.canceled = FALSE
        self.druid.show_all()
        self.entries = {
            "localNetworkEntry" : "LocalNetwork",
            "localSubnetEntry" : "LocalNetmask",
            "localGatewayEntry" : "LocalGateway",
            "remoteNetworkEntry" : "RemoteNetwork",
            "remoteSubnetEntry" : "RemoteNetmask",
            "remoteGatewayEntry" : "RemoteGateway",
            "remoteIPEntry" : "RemoteIPAddress",
            "AHKeyEntry" : "AHKey",
            "ESPKeyEntry" : "ESPKey",
            }
            
        for key, val in self.entries.items():
            if val:
                widget = self.xml.get_widget(key)
                if widget:
                    widget.set_text(getattr(self.ipsec, val) or "")
                         

    def on_ipsecDruidConnectionTypePage_prepare(self, druid_page, druid):
        if self.ipsec.ConnectionType == "Host2Host":
            self.xml.get_widget("hosttohostEncryptionRadio").set_active(TRUE)
        else:
            self.xml.get_widget("nettonetEncryptionRadio").set_active(TRUE)
            
        return TRUE

    def on_ipsecDruidConnectionTypePage_next(self, druid_page, druid):
        if self.xml.get_widget("hosttohostEncryptionRadio").get_active():
            self.ipsec.ConnectionType = "Host2Host"
            self.xml.get_widget("ipsecDruidLocalNetworkPage").hide()
        else:
            self.ipsec.ConnectionType = "Net2Net"
            self.xml.get_widget("ipsecDruidLocalNetworkPage").show()
            
    def on_ipsecDruidEncryptionModePage_prepare(self, druid_page, druid):
        if self.ipsec.EncryptionMode == "manual":
            self.xml.get_widget("manualEncryptionRadio").set_active(TRUE)
        else:
            self.xml.get_widget("automaticEncryptionRadio").set_active(TRUE)
        return TRUE

    def on_ipsecDruidEncryptionModePage_next(self, druid_page, druid):
        if self.xml.get_widget("manualEncryptionRadio").get_active():
            self.ipsec.EncryptionMode = "manual"
            for widget in [ "ESPKeyLabel", "ESPKeyEntry", "ESPKeyButton" ]:
                self.xml.get_widget(widget).show()
        else:
            self.ipsec.EncryptionMode = "auto"
            for widget in [ "ESPKeyLabel", "ESPKeyEntry", "ESPKeyButton" ]:
                self.xml.get_widget(widget).hide()
                        
    def on_ipsecDruidLocalNetworkPage_prepare(self, druid_page, druid):
        return TRUE
    
    def on_ipsecDruidRemoteNetworkPage_prepare(self, druid_page, druid):
        return TRUE
    
    def on_ipsecDruidKeysPage_prepare(self, druid_page, druid):
        return TRUE
    
    def on_ipsecDruidFinishPage_prepare(self, druid_page, druid):
        for key, val in self.entries.items():
            widget = self.xml.get_widget(key)            
            entry = (widget and widget.get_text()) or None
            if entry:
                setattr(self.ipsec, val, entry)
        
        s = _("You have selected the following information:") + "\n\n"
        s += str(self.ipsec)
        druid_page.set_text(s)
        return TRUE
    
    def on_ipsecDruidFinishPage_finish(self, druid_page, druid):
        self.druid.hide()
        self.druid.destroy()
        gtk.mainquit()
        return TRUE
    
    def on_ipsecDruid_cancel(self, *args):
        self.canceled = TRUE
        self.druid.destroy()
        gtk.mainquit()
        return TRUE

    def on_generateAHKeyButton_clicked(self, *args):
        command = '/bin/sh'
        (status , key ) = gtkExecWithCaptureStatus(command = command,
                                                   argv = [command, '-c',
                                                           '(ps aux|md5sum; ps alx|md5sum) | tr -cd 0-9 2>/dev/null'])
        
        widget = self.xml.get_widget("AHKeyEntry")
        if key:
            widget.set_text(key)
        
    def on_generateESPKeyButton_clicked(self, *args):
        command = '/bin/sh'
        (status , key ) = gtkExecWithCaptureStatus(command = command,
                                                   argv = [command, '-c',
                                                           '(ps aux|md5sum; ps alx|md5sum) | tr -cd 0-9 2>/dev/null'])
        
        widget = self.xml.get_widget("ESPKeyEntry")
        if key:
            widget.set_text(key)

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/07/01 13:00:04 $"
__version__ = "$Revision: 1.2 $"