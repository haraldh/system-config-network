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
import re

from NCDeviceList import *
from NCCallback import *
from NCHardwareList import *

from provider import *
from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class DialupDialog:
    def __init__(self, device, xml_main = None, xml_basic = None):
        self.xml_main = xml_main
        self.xml_basic = xml_basic
        self.device = device
        self.edit = FALSE
        
        glade_file = "dialupconfig.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = "/usr/share/redhat-config-network/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")

        self.xml.signal_autoconnect(
            {
            "on_chooseButton_clicked" : self.on_chooseButton_clicked,
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_helpButton_clicked" : self.on_helpButton_clicked,
            "on_dialingRuleCB_toggled" : self.on_dialingRuleCB_toggled,
            "on_callbackCB_toggled" : self.on_callbackCB_toggled,
            "on_pppOptionEntry_changed" : self.on_pppOptionEntry_changed,
            "on_pppOptionAddButton_clicked" : self.on_pppOptionAddButton_clicked,
            "on_pppOptionList_select_row" : self.on_pppOptionList_select_row,
            "on_ipppOptionList_unselect_row" : self.on_ipppOptionList_unselect_row,
            "on_pppOptionDeleteButton_clicked" : self.on_pppOptionDeleteButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        self.noteBook = self.xml.get_widget("dialupNotebook")
        self.load_icon("network.xpm")
        self.dialog.set_close(TRUE)

    def load_icon(self, pixmap_file, widget = None):
        if not os.path.exists(pixmap_file):
            pixmap_file = "pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "../pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "/usr/share/redhat-config-network/" + pixmap_file
        if not os.path.exists(pixmap_file):
            return

        pix, mask = gtk.create_pixmap_from_xpm(self.dialog, None, pixmap_file)
        gtk.GtkPixmap(pix, mask)

        if widget:
            widget.set(pix, mask)
        else:
            self.dialog.set_icon(pix, mask)

    def hydrate(self):
        hardwarelist = getHardwareList()
        if self.device.Dialup.ProviderName:
            self.xml.get_widget("providerName").set_text(self.device.Dialup.ProviderName)
        if self.device.Dialup.Login:
            self.xml.get_widget("loginNameEntry").set_text(self.device.Dialup.Login)
        if self.device.Dialup.Password:
            self.xml.get_widget("passwordEntry").set_text(self.device.Dialup.Password)
        if self.device.Dialup.Areacode:
            self.xml.get_widget("areaCodeEntry").set_text(self.device.Dialup.Areacode)
        if self.device.Dialup.PhoneNumber:
            self.xml.get_widget("phoneEntry").set_text(self.device.Dialup.PhoneNumber)
        if self.device.Dialup.Prefix:
            self.xml.get_widget("prefixEntry").set_text(self.device.Dialup.Prefix)
        if self.device.Dialup.Areacode and self.device.Dialup.Prefix and self.device.Dialup.Regioncode:
            self.xml.get_widget("dialingRuleCB").set_active(len(self.device.Dialup.Areacode) >0 or
                                                            len(self.device.Dialup.Prefix) >0 or
                                                            len(self.device.Dialup.Regioncode) >0)
        if self.device.Dialup.Regioncode and len(self.device.Dialup.Regioncode) >0:
            self.xml.get_widget("countryCodeEntry").set_text(self.device.Dialup.Regioncode)

        if self.device.Dialup.Authentication and len(self.device.Dialup.Authentication) >0:
            self.xml.get_widget("authEntry").set_text(self.device.Dialup.Authentication)

        if self.device.Dialup.Compression:
            if self.device.Dialup.Compression.VJTcpIp:
                self.xml.get_widget("HeaderCompressionCB").set_active(self.device.Dialup.Compression.VJTcpIp == true)
            if self.device.Dialup.Compression.VJID:
                self.xml.get_widget("connectionCompressionCB").set_active(self.device.Dialup.Compression.VJID == true)
            if self.device.Dialup.Compression.AdressControl:
                self.xml.get_widget("acCompressionCB").set_active(self.device.Dialup.Compression.AdressControl == true)

        if self.device.Dialup.PPPOptions:
            self.xml.get_widget("pppOptionList").set_sensitive(len(self.device.Dialup.PPPOptions)>0)
            for plist in self.device.Dialup.PPPOptions:
                self.xml.get_widget("pppOptionList").append([plist])

        
    def dehydrate(self):
        self.device.Dialup.ProviderName = self.xml.get_widget("providerName").get_text()
        self.device.Dialup.Login = self.xml.get_widget("loginNameEntry").get_text()
        self.device.Dialup.Password = self.xml.get_widget("passwordEntry").get_text()
        self.device.Dialup.Areacode = self.xml.get_widget("areaCodeEntry").get_text()
        self.device.Dialup.PhoneNumber = self.xml.get_widget("phoneEntry").get_text()
        self.device.Dialup.Prefix = self.xml.get_widget("prefixEntry").get_text()
        self.device.Dialup.Regioncode = self.xml.get_widget("countryCodeEntry").get_text()
        
    def on_Dialog_delete_event(self, *args):
        pass
    
    def on_okButton_clicked(self, button):
        pass
    
    def on_cancelButton_clicked(self, button):
        pass
    
    def on_helpButton_clicked(self, button):
        pass

    def on_msnEntry_changed (self, *args):
        pass

    def on_dialingRuleCB_toggled(self, check):
        prefixEntry = self.xml.get_widget("prefixEntry")
        prefixEntry.set_sensitive(check["active"])
        self.xml.get_widget("areaCodeEntry").set_sensitive(check["active"])
        self.xml.get_widget("countryCodeCombo").set_sensitive(check["active"])
        if check["active"]:
            prefixEntry.grab_focus()
        else:
            self.xml.get_widget("phoneEntry").grab_focus()

    def on_callbackCB_toggled(self, check):
        self.xml.get_widget("callbackFrame").set_sensitive(check["active"])
        self.xml.get_widget("dialinNumberEntry").grab_focus()
    
    def on_prefixEntry_changed (self, *args):
        pass

    def on_areaCodeEntry_changed (self, *args):
        pass

    def on_phoneEntry_changed (self, *args):
        pass

    def on_countryCodeEntry_changed (self, *args):
        pass

    def on_authMenu_enter (self, *args):
        pass

    def on_dialupProviderNameEntry_changed (self, *args):
        pass

    def on_dialupLoginNameEntry_activate (self, *args):
        pass

    def on_dialupPasswordEntry_changed (self, *args):
        pass

    def on_HeaderCompressionCB_toggled (self, *args):
        pass

    def on_connectionCompressionCB_toggled (self, *args):
        pass

    def on_acCompressionCB_toggled (self, *args):
        pass

    def on_pcCompressionCB_toggled (self, *args):
        pass

    def on_bsdCompressionCB_toggled (self, *args):
        pass

    def on_cppCompressionCB_toggled (self, *args):
        pass

    def on_pppOptionEntry_changed (self, entry):
        option = string.strip(entry.get_text())
        self.xml.get_widget("pppOptionAddButton").set_sensitive(len(option) > 0)

    def on_pppOptionAddButton_clicked (self, button):
        entry = self.xml.get_widget("pppOptionEntry")
        self.xml.get_widget("pppOptionList").set_sensitive(TRUE)
        self.xml.get_widget("pppOptionList").append([entry.get_text()])
        entry.set_text("")
        entry.grab_focus()
    
    def on_pppOptionList_select_row(self, clist, r, c, event):
        self.xml.get_widget ("pppOptionDeleteButton").set_sensitive (TRUE)
    
    def on_ipppOptionList_unselect_row (self, clist, r, c, event):
        self.xml.get_widget("pppOptionDeleteButton").set_sensitive(FALSE)

    def on_pppOptionDeleteButton_clicked(self, button):
        clist = self.xml.get_widget("pppOptionList")
        if clist.selection:
            clist.remove(clist.selection[0])

    def on_chooseButton_clicked(self, button):
        dialog = providerDialog(self.xml_main, self.xml_basic, self.xml)

    def set_title(self, title = _("Dialup Configuration")):
        self.dialog.set_title(title)
        

class ISDNDialupDialog(DialupDialog):
    def __init__(self, device, xml_main = None, xml_basic = None):
        DialupDialog.__init__(self, device, xml_main, xml_basic)

        self.noteBook.get_nth_page(4).hide()
        self.dialog.set_title(_("ISDN Dialup Configuration"))
        self.hydrate()
        self.hydrateISDN()

    def on_chooseButton_clicked(self, button):
        dialog = ISDNproviderDialog(self.xml_main, self.xml_basic, self.xml)

    def on_okButton_clicked(self, button):
        self.dehydrate()
        self.dehydrateISDN()
		
    def hydrateISDN(self):
        if self.device.Dialup.Callback != None:
            self.xml.get_widget("callbackCB").set_active(self.device.Dialup.Callback != None)
            self.xml.get_widget("dialinNumberEntry").set_text(self.device.Dialup.Callback.Number)
            self.xml.get_widget("callbackDelaySB").set_value(self.device.Dialup.Callback.Delay)
            self.xml.get_widget("allowDialinNumberCB").set_active(self.device.Dialup.Secure == true)
            self.xml.get_widget("cbcpCB").set_active(self.device.Dialup.Callback.CBCP == true)
        if self.device.Dialup.HangupTimeout:
            self.xml.get_widget("hangupTimeoutISDNSB").set_value(self.device.Dialup.HangupTimeout)
        if self.device.Dialup.DialMode:
            self.xml.get_widget("dialModeISDNEntry").set_text(self.device.Dialup.DialMode)
        if self.device.Dialup.EncapMode:
            self.xml.get_widget("encapModeEntry").set_text(self.device.Dialup.EncapMode)
        if self.device.Dialup.MSN:
            self.xml.get_widget("msnEntry").set_text(str(self.device.Dialup.MSN))
        if self.device.Dialup.ChannelBundling:
            self.xml.get_widget("channelBundlingCB").set_active(self.device.Dialup.ChannelBundling == true)
            
    def dehydrateISDN(self):
        devicelist = getDeviceList()
        
        device_list_raw = []
        device_list_sync = []

        if self.xml.get_widget("encapModeEntry").get_text() == "sync PPP":
            self.device.Dialup.EncapMode = "syncppp"
        else:
            self.device.Dialup.EncapMode = "rawip"
        
        if not self.device.Device:
            for i in devicelist:
                if i.Type == 'ISDN':
                    if i.Dialup.EncapMode == 'syncppp':
                        device_list_sync.append(i.Device)
                    else:
                        device_list_raw.append(i.Device)
            for i in xrange(100):
                if self.device.Dialup.EncapMode == 'syncppp':
                    if device_list_sync.count("ippp"+str(i)) == 0:
                        self.device.Device = "ippp" + str(i)
                        break
                else:
                    if device_list_raw.count("isdn"+str(i)) == 0:
                        self.device.Device = "isdn" + str(i)
                        break

        if self.xml.get_widget("callbackCB").get_active():
            self.device.Dialup.createCallback()
            self.device.Dialup.Callback.Number = self.xml.get_widget("dialinNumberEntry").get_text()
            self.device.Dialup.Callback.Delay = self.xml.get_widget("callbackDelaySB").get_value_as_int()
            if self.xml.get_widget("allowDialinNumberCB")["active"]:
                self.device.Dialup.Secure = true
            else:
                self.device.Dialup.Secure = false
                
            if self.xml.get_widget("cbcpCB")["active"]:
                self.device.Dialup.Callback.CBCP = true
            else:
                self.device.Dialup.Callback.CBCP = false
        
        self.device.Dialup.HangupTimeout = self.xml.get_widget("hangupTimeoutISDNSB").get_value_as_int()
        self.device.Dialup.DialMode = self.xml.get_widget("dialModeISDNEntry").get_text()
        self.device.Dialup.EncapMode = self.xml.get_widget("encapModeEntry").get_text()
        self.device.Dialup.MSN = self.xml.get_widget("msnEntry").get_text()
        if self.xml.get_widget("channelBundlingCB")['active']:
            self.device.Dialup.ChannelBundling = true
        else:
            self.device.Dialup.ChannelBundling = false

        print "Device:", self.device.Device
        
class ModemDialupDialog(DialupDialog):
    def __init__(self, device, xml_main = None, xml_basic = None):
        DialupDialog.__init__(self, device, xml_main, xml_basic)
        
        self.dialog.set_title(_("Modem Dialup Configuration"))
        for i in [1,5]:
            self.noteBook.get_nth_page(i).hide()

        self.hydrate()
        self.hydrateModem()

    def on_chooseButton_clicked(self, button):
        dialog = ModemproviderDialog(self.xml_main, self.xml_basic, self.xml)

    def on_okButton_clicked(self, button):
        self.dehydrate()
        self.dehydrateModem()

    def hydrateModem(self):
		
        hardwarelist = getHardwareList()
        devicelist = []
        for hw in hardwarelist:
            if hw.Type == 'Modem':
                devicelist.append(hw.Name)
                continue

        if devicelist:
            self.xml.get_widget("modemPortCombo").set_popdown_strings(devicelist)

        if self.device.Dialup.HangupTimeout:
            self.xml.get_widget("hangupTimeoutSB").set_value(self.device.Dialup.HangupTimeout)
        if self.device.Dialup.DialMode:
            self.xml.get_widget("dialModeEntry").set_text(self.device.Dialup.DialMode)
        if self.device.Dialup.InitStrings:
            self.xml.get_widget("modemInitEntry").set_text("text")
        if self.device.Name:
            self.xml.get_widget("modemPortEntry").set_text(self.device.Name)

    def dehydrateModem(self):
        pass


# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = DialupDialog()
    window.run()
    gtk.mainloop()
