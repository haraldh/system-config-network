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

from deviceconfig import deviceConfigDialog
from NCDeviceList import *
from NCCallback import *
from NCHardwareList import *
from NC_functions import *

from provider import *
from gtk import TRUE
from gtk import FALSE

##
## I18N
##
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
_=gettext.gettext

class DialupDialog(deviceConfigDialog):
    def __init__(self, device, xml_main = None):
        glade_file = "dialupconfig.glade"
        deviceConfigDialog.__init__(self, glade_file,
                                    device, xml_main)
        self.edit = FALSE

        self.xml.signal_autoconnect(
            {
            "on_chooseButton_clicked" : self.on_chooseButton_clicked,
            "on_helpButton_clicked" : self.on_helpButton_clicked,
            "on_callbackCB_toggled" : self.on_callbackCB_toggled,
            "on_pppOptionEntry_changed" : self.on_pppOptionEntry_changed,
            "on_pppOptionAddButton_clicked" : self.on_pppOptionAddButton_clicked,
            "on_pppOptionList_select_row" : self.on_pppOptionList_select_row,
            "on_ipppOptionList_unselect_row" : self.on_ipppOptionList_unselect_row,
            "on_pppOptionDeleteButton_clicked" : self.on_pppOptionDeleteButton_clicked
            })

        self.noteBook = self.xml.get_widget("dialupNotebook")

    def hydrate(self):
        deviceConfigDialog.hydrate(self)
        hardwarelist = getHardwareList()

        dialup = self.device.Dialup
        
        if dialup.ProviderName != None:
            self.xml.get_widget("providerName").set_text(dialup.ProviderName)
        if dialup.Login != None:
            self.xml.get_widget("loginNameEntry").set_text(dialup.Login)
        if dialup.Password != None:
            self.xml.get_widget("passwordEntry").set_text(dialup.Password)

        if dialup.Areacode != None:
            self.xml.get_widget("areaCodeEntry").set_text(dialup.Areacode)
        if dialup.PhoneNumber != None:
            self.xml.get_widget("phoneEntry").set_text(dialup.PhoneNumber)
        if dialup.Prefix != None:
            self.xml.get_widget("prefixEntry").set_text(dialup.Prefix)

        if dialup.Authentication and len(dialup.Authentication) >0:
            self.xml.get_widget("authEntry").set_text(dialup.Authentication)

        if dialup.Compression:
            self.xml.get_widget("headerCompressionCB").set_active(dialup.Compression.VJTcpIp == true)
            self.xml.get_widget("connectionCompressionCB").set_active(dialup.Compression.VJID == true)
            self.xml.get_widget("acCompressionCB").set_active(dialup.Compression.AdressControl == true)
            self.xml.get_widget("pfCompressionCB").set_active(dialup.Compression.ProtoField == true)
            self.xml.get_widget("bsdCompressionCB").set_active(dialup.Compression.BSD == true)
            self.xml.get_widget("cppCompressionCB").set_active(dialup.Compression.CCP == true)

        if dialup.PPPOptions:
            widget = self.xml.get_widget("pppOptionList")
            widget.clear()
            widget.set_sensitive(len(dialup.PPPOptions)>0)
            for plist in dialup.PPPOptions:
                widget.append([plist])
        
    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        dialup = self.device.Dialup

        dialup.ProviderName = self.xml.get_widget("providerName").get_text()
        dialup.Login = self.xml.get_widget("loginNameEntry").get_text()
        dialup.Password = self.xml.get_widget("passwordEntry").get_text()
        dialup.Areacode = self.xml.get_widget("areaCodeEntry").get_text()
        dialup.Prefix = self.xml.get_widget("prefixEntry").get_text()
        dialup.PhoneNumber = self.xml.get_widget("phoneEntry").get_text()

        if not dialup.Compression:
            dialup.createCompression()
            
        dialup.Compression.VJTcpIp = self.xml.get_widget("headerCompressionCB").get_active()
        dialup.Compression.VJID = self.xml.get_widget("connectionCompressionCB").get_active()
        dialup.Compression.AdressControl = self.xml.get_widget("acCompressionCB").get_active()
        dialup.Compression.ProtoField = self.xml.get_widget("pfCompressionCB").get_active()
        dialup.Compression.BSD = self.xml.get_widget("bsdCompressionCB").get_active()
        dialup.Compression.CCP = self.xml.get_widget("cppCompressionCB").get_active()

        dialup.PPPOptions = None
        dialup.createPPPOptions()
        clist = self.xml.get_widget("pppOptionList")
        for i in xrange (clist.rows):
            dialup.PPPOptions.append(clist.get_text (i, 0))
            
    def on_helpButton_clicked(self, button):
        pass

    def on_msnEntry_changed (self, *args):
        pass

    def on_callbackCB_toggled(self, check):
        self.xml.get_widget("callbackFrame").set_sensitive(check["active"])
        self.xml.get_widget("dialinNumberEntry").grab_focus()
    
    def on_prefixEntry_changed (self, *args):
        pass

    def on_areaCodeEntry_changed (self, *args):
        pass

    def on_phoneEntry_changed (self, *args):
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
        dialog = providerDialog(self.device, self.xml_main, self.xml)
        
    def set_title(self, title = _("Dialup Configuration")):
        self.dialog.set_title(title)



class ISDNDialupDialog(DialupDialog):
    def __init__(self, device, xml_main = None):
        DialupDialog.__init__(self, device, xml_main)

        page = self.noteBook.page_num(self.xml.get_widget ("modemTab"))
        self.noteBook.get_nth_page(page).hide()        
        
        self.dialog.set_title(_("ISDN Dialup Configuration"))

    def on_chooseButton_clicked(self, button):
        dialog = ISDNproviderDialog(self.device, self.xml_main, self.xml)
        dl = dialog.xml.get_widget("Dialog")
        dl.run()
        DialupDialog.hydrate(self)
        self.hydrate()

    def hydrate(self):
        DialupDialog.hydrate(self)

        dialup = self.device.Dialup
        
        if dialup.Callback and dialup.Callback.Type != 'off':
            self.xml.get_widget("callbackCB").set_active(true)
            self.xml.get_widget("callbackFrame").set_sensitive(true)
            self.xml.get_widget("dialinNumberEntry").set_text(dialup.Callback.Number)
            self.xml.get_widget("callbackDelaySB").set_value(dialup.Callback.Delay)
            self.xml.get_widget("allowDialinNumberCB").set_active(dialup.Secure)
            self.xml.get_widget("cbcpCB").set_active(dialup.Callback.Compression)
        if dialup.HangupTimeout:
            self.xml.get_widget("hangupTimeoutISDNSB").set_value(dialup.HangupTimeout)
        if dialup.DialMode:
            self.xml.get_widget("dialModeISDNEntry").set_text(dialup.DialMode)
        if dialup.EncapMode == "raw IP":
            self.xml.get_widget("encapModeEntry").set_text('raw IP')
        else:
            self.xml.get_widget("encapModeEntry").set_text('sync PPP')
        if dialup.MSN:
            self.xml.get_widget("msnEntry").set_text(str(dialup.MSN))
        if dialup.ChannelBundling:
            self.xml.get_widget("channelBundlingCB").set_active(dialup.ChannelBundling == true)
        if dialup.Authentication:
            self.xml.get_widget("authEntry").set_text(dialup.Authentication)

    def dehydrate(self):
        DialupDialog.dehydrate(self)
        
        dialup = self.device.Dialup
        
        if self.xml.get_widget("encapModeEntry").get_text() == "sync PPP":
            dialup.EncapMode = "syncppp"
            self.device.Device = "ippp"
        else:
            dialup.EncapMode = "rawip"
            self.device.Device = "isdn"

        if not dialup.Callback: dialup.createCallback()
        if self.xml.get_widget("callbackCB").get_active():
            dialup.Callback.Type = "out"
            dialup.Callback.Number = self.xml.get_widget("dialinNumberEntry").get_text()
            dialup.Callback.Delay = self.xml.get_widget("callbackDelaySB").get_value_as_int()
            dialup.Callback.Hup = 3
            dialup.Secure = self.xml.get_widget("allowDialinNumberCB").get_active()
            dialup.Callback.Compression = self.xml.get_widget("cbcpCB").get_active()
        else:
            dialup.Callback.Type = "off"

        dialup.HangupTimeout = self.xml.get_widget("hangupTimeoutISDNSB").get_value_as_int()
        dialup.DialMode = self.xml.get_widget("dialModeISDNEntry").get_text()
        dialup.MSN = self.xml.get_widget("msnEntry").get_text()
        dialup.ChannelBundling = self.xml.get_widget("channelBundlingCB").get_active()
        dialup.Authentication = self.xml.get_widget("authEntry").get_text()


        
class ModemDialupDialog(DialupDialog):
    def __init__(self, device, xml_main = None):
        DialupDialog.__init__(self, device, xml_main)
        
        self.dialog.set_title(_("Modem Dialup Configuration"))
        page = self.noteBook.page_num(self.xml.get_widget ("isdnTab"))
        self.noteBook.get_nth_page(page).hide()        
        page = self.noteBook.page_num(self.xml.get_widget ("callbackTab"))
        self.noteBook.get_nth_page(page).hide()
        
    def on_chooseButton_clicked(self, button):
        dialog = ModemproviderDialog(self.device, self.xml_main, self.xml)
        dl = dialog.xml.get_widget("Dialog")
        dl.run()
        DialupDialog.hydrate(self)
        self.hydrate()
        
    def hydrate(self):
        DialupDialog.hydrate(self)
        hardwarelist = getHardwareList()
        devicelist = []
        for hw in hardwarelist:
            if hw.Type == 'Modem':
                devicelist.append(hw.Name)
                continue

        if devicelist:
            self.xml.get_widget("modemPortCombo").set_popdown_strings(devicelist)

        dialup = self.device.Dialup
        if dialup.HangupTimeout:
            self.xml.get_widget("hangupTimeoutSB").set_value(dialup.HangupTimeout)
        if dialup.DialMode:
            self.xml.get_widget("dialModeEntry").set_text(dialup.DialMode)

        if dialup.InitStrings:
           s = ""
           widget = self.xml.get_widget("modemInitEntry")
           for plist in dialup.InitStrings:
               if (len(plist) >= 2) and (plist[:2] == 'AT') and len(s):
                   plist = plist[2:]
               s = s + plist
           widget.set_text(s)

        if dialup.Persist:
            self.xml.get_widget("persistCB").set_active(dialup.Persist)
        if dialup.DefRoute:
            self.xml.get_widget("defrouteCB").set_active(dialup.DefRoute)
        if self.device.Name:
            self.xml.get_widget("modemPortEntry").set_text(self.device.Name)

        self.xml.get_widget("stupidModeCB").set_active(self.device.Dialup.StupidMode == true)

    def dehydrate(self):
        DialupDialog.dehydrate(self)

        dialup = self.device.Dialup
        
        dialup.HangupTimeout = self.xml.get_widget("hangupTimeoutSB").get_value()
        dialup.DialMode = self.xml.get_widget("dialModeEntry").get_text()
        dialup.InitStrings = self.xml.get_widget("modemInitEntry").get_text()
        self.device.Name = self.xml.get_widget("modemPortEntry").get_text()

        if not self.device.Device:
            self.device.Device = "modem"

        dialup.Persist = self.xml.get_widget("persistCB").get_active()
        dialup.DefRoute = self.xml.get_widget("defrouteCB").get_active()

        dialup.InitStrings = None
        dialup.createInitStrings()
        for i in string.split(self.xml.get_widget("modemInitEntry").get_text()):
            dialup.InitStrings.append(i)

        dialup.StupidMode = (self.xml.get_widget("stupidModeCB").get_active() == true)


# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = DialupDialog()
    window.run()
    gtk.mainloop()
