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
import sharedtcpip

from deviceconfig import deviceConfigDialog
from netconfpkg import NCDevIsdn
from netconfpkg import NCDevModem
from netconfpkg.NCDeviceList import *
from netconfpkg.NCCallback import *
from netconfpkg.NCHardwareList import *
from netconfpkg.NCDialup import *
from netconfpkg.gui.GUI_functions import *
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg.gui.tonline import TonlineDialog
from provider import *
from gtk import TRUE
from gtk import FALSE


class DialupDialog(deviceConfigDialog):
    def __init__(self, device):
        glade_file = "sharedtcpip.glade"
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file
        self.sharedtcpip_xml = gtk.glade.XML (glade_file, None,
                                                  domain=PROGNAME)

        glade_file = "dialupconfig.glade"
        deviceConfigDialog.__init__(self, glade_file,
                                    device)
        self.edit = FALSE

        xml_signal_autoconnect(self.xml, 
            {
            "on_chooseButton_clicked" : self.on_chooseButton_clicked,
            "on_helpButton_clicked" : self.on_helpButton_clicked,
            "on_callbackCB_toggled" : self.on_callbackCB_toggled,
            "on_pppOptionEntry_changed" : self.on_pppOptionEntry_changed,
            "on_pppOptionAddButton_clicked" : \
            self.on_pppOptionAddButton_clicked,
            "on_pppOptionList_select_row" : self.on_pppOptionList_select_row,
            "on_ipppOptionList_unselect_row" : \
            self.on_ipppOptionList_unselect_row,
            "on_pppOptionDeleteButton_clicked" : \
            self.on_pppOptionDeleteButton_clicked,
            "on_tonlineButton_clicked" : self.on_tonlineButton_clicked,
            })

        self.noteBook = self.xml.get_widget("dialupNotebook")
        self.xml.get_widget ("pppOptionList").column_titles_passive ()

        window = self.sharedtcpip_xml.get_widget ('dhcpWindow')
        frame = self.sharedtcpip_xml.get_widget ('dhcpFrame')
        vbox = self.xml.get_widget ('generalVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.dhcp_init (self.sharedtcpip_xml, self.device)

        window = self.sharedtcpip_xml.get_widget ('routeWindow')
        frame = self.sharedtcpip_xml.get_widget ('routeFrame')
        vbox = self.xml.get_widget ('routeVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.route_init (self.sharedtcpip_xml, self.device, self.dialog)
        self.hydrate ()

    def hydrate(self):
        deviceConfigDialog.hydrate(self)
        hardwarelist = getHardwareList()

        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)

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

        if dialup.Compression:
            self.xml.get_widget("headerCompressionCB").set_active(\
                dialup.Compression.VJTcpIp == true)
            self.xml.get_widget("connectionCompressionCB").set_active(\
                dialup.Compression.VJID == true)
            self.xml.get_widget("acCompressionCB").set_active(\
                dialup.Compression.AdressControl == true)
            self.xml.get_widget("pfCompressionCB").set_active(\
                dialup.Compression.ProtoField == true)
            self.xml.get_widget("bsdCompressionCB").set_active(\
                dialup.Compression.BSD == true)
            self.xml.get_widget("cppCompressionCB").set_active(\
                dialup.Compression.CCP == true)

        if dialup.PPPOptions:
            widget = self.xml.get_widget("pppOptionList")
            widget.clear()
            widget.set_sensitive(len(dialup.PPPOptions)>0)
            for plist in dialup.PPPOptions:
                widget.append([plist])

    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)
        dialup = self.device.Dialup

        dialup.ProviderName = self.xml.get_widget("providerName").get_text()
        dialup.Login = self.xml.get_widget("loginNameEntry").get_text()
        dialup.Password = self.xml.get_widget("passwordEntry").get_text()
        dialup.Areacode = self.xml.get_widget("areaCodeEntry").get_text()
        dialup.Prefix = self.xml.get_widget("prefixEntry").get_text()
        dialup.PhoneNumber = self.xml.get_widget("phoneEntry").get_text()

        if not dialup.Compression:
            dialup.createCompression()
            
        dialup.Compression.VJTcpIp = self.xml.get_widget(\
            "headerCompressionCB").get_active()
        dialup.Compression.VJID = self.xml.get_widget(\
            "connectionCompressionCB").get_active()
        dialup.Compression.AdressControl = self.xml.get_widget(\
            "acCompressionCB").get_active()
        dialup.Compression.ProtoField = self.xml.get_widget(\
            "pfCompressionCB").get_active()
        dialup.Compression.BSD = self.xml.get_widget(\
            "bsdCompressionCB").get_active()
        dialup.Compression.CCP = self.xml.get_widget(\
            "cppCompressionCB").get_active()

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
        self.xml.get_widget("callbackFrame").set_sensitive(check.get_active())
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
        self.xml.get_widget("pppOptionAddButton").set_sensitive(\
            len(option) > 0)

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
        dialog = providerDialog(self.device)
        
    def set_title(self, title = _("Dialup Configuration")):
        self.dialog.set_title(title)

    def on_tonlineButton_clicked(self, *args):
        self.dehydrate()
        dialup = self.device.Dialup
        dialog = TonlineDialog(dialup.Login, dialup.Password)
        dl = dialog.xml.get_widget ("Dialog")
        
        dl.set_transient_for(self.dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        
        if dl.run() != gtk.RESPONSE_OK:
            dl.destroy()        
            return

        dl.destroy()
        dialup.Login = dialog.login
        dialup.Password = dialog.password
        self.xml.get_widget("loginNameEntry").set_text(dialup.Login)
        self.xml.get_widget("passwordEntry").set_text(dialup.Password)
        if not self.xml.get_widget("providerName").get_text():
            self.xml.get_widget("providerName").set_text("T-Online")

 
class ISDNDialupDialog(DialupDialog):
    def __init__(self, device):
        DialupDialog.__init__(self, device)

        page = self.noteBook.page_num(self.xml.get_widget ("modemTab"))
        self.noteBook.get_nth_page(page).hide()

        self.dialog.set_title(_("ISDN Dialup Configuration"))

    def on_chooseButton_clicked(self, button):
        dialog = ISDNproviderDialog(self.device)
        dl = dialog.xml.get_widget("Dialog")
        dl.set_transient_for(self.dialog)
        dl.run()
        dl.destroy()        
        DialupDialog.hydrate(self)
        self.hydrate()

    def hydrate(self):
        DialupDialog.hydrate(self)

        dialup = self.device.Dialup

        omenu = self.xml.get_widget("CallbackMode")
        omenu.remove_menu()
        menu = gtk.Menu()
        history = 0
        for txt in [_('in'), _('out')]:
            item = gtk.MenuItem (txt)
            item.show()
            menu.append (item)
        omenu.set_menu (menu)
        omenu.show_all()

        if dialup.PhoneInNumber:
            self.xml.get_widget("dialinNumberEntry").set_text(\
                dialup.PhoneInNumber)

        if dialup.Secure:
            self.xml.get_widget("allowDialinNumberCB").set_active(\
                dialup.Secure)
            
        if dialup.Callback and dialup.Callback.Type != 'off':
            self.xml.get_widget("callbackCB").set_active(true)
            self.xml.get_widget("callbackFrame").set_sensitive(true)
            if dialup.Callback.Type == 'in':
                self.xml.get_widget('CallbackMode').set_history(0)
            else:
                self.xml.get_widget('CallbackMode').set_history(1)
            self.xml.get_widget('CallbackMode').show_all()
            
            self.xml.get_widget("callbackDelaySB").set_value(\
                dialup.Callback.Delay)
            self.xml.get_widget("cbcpCB").set_active(\
                dialup.Callback.Compression)

        if dialup.HangupTimeout:
            self.xml.get_widget("hangupTimeoutISDNSB").set_value(\
                dialup.HangupTimeout)
            
        if dialup.DialMode:
            if dialup.DialMode == DM_AUTO:
                dialmode = DialModes[DM_AUTO]
            else:
                dialmode = DialModes[DM_MANUAL]
        else:
            dialmode = DialModes[DM_MANUAL]
            
        self.xml.get_widget("dialModeISDNEntry").set_text(dialmode)
        
        if dialup.EncapMode == 'rawip':
            self.xml.get_widget("encapModeEntry").set_text(_('raw IP'))
        else:
            self.xml.get_widget("encapModeEntry").set_text(_('sync PPP'))

        if dialup.MSN:
            self.xml.get_widget("msnEntry").set_text(str(dialup.MSN))

        if dialup.DefRoute != None:
            self.xml.get_widget("defrouteISDNCB").set_active(dialup.DefRoute)
        
        if dialup.ChannelBundling:
            self.xml.get_widget("channelBundlingCB").set_active(\
                dialup.ChannelBundling == true)
        if dialup.Authentication:
            if dialup.Authentication == '+pap -chap':
                auth = _('pap')
            elif dialup.Authentication == '-pap +chap':
                auth = _('chap')
            elif dialup.Authentication == '+chap +pap' or \
                     dialup.Authentication == '+pap +chap':
                auth = _('chap+pap')
            else:
                auth = _('none')
            self.xml.get_widget("authEntry").set_text(auth)

    def dehydrate(self):
        DialupDialog.dehydrate(self)
        
        dialup = self.device.Dialup
        
        self.device.Name = self.xml.get_widget('deviceNameEntry').get_text()

        encap_mode_old = dialup.EncapMode
        if self.xml.get_widget("encapModeEntry").get_text() == _("sync PPP"):
            dialup.EncapMode = "syncppp"
        else:
            dialup.EncapMode = "rawip"

        # get free ISDN device if encap mode is changed
        if encap_mode_old != dialup.EncapMode:
            self.device.Device = getNewDialupDevice(\
                getDeviceList(), self.device)

        dialup.PhoneInNumber = self.xml.get_widget(\
            "dialinNumberEntry").get_text()
        dialup.Secure = self.xml.get_widget("allowDialinNumberCB").get_active()
        
        if not dialup.Callback: dialup.createCallback()
        if self.xml.get_widget("callbackCB").get_active():
            if self.xml.get_widget('CallbackMode').get_child().get_label() == \
                   _('in'):
                dialup.Callback.Type = 'in'
            else:
                dialup.Callback.Type = 'out'
            dialup.Callback.Delay = self.xml.get_widget(\
                "callbackDelaySB").get_value_as_int()
            dialup.Callback.Hup = false
            dialup.Callback.Compression = self.xml.get_widget(\
                "cbcpCB").get_active()
        else:
            dialup.Callback.Type = "off"

        dialup.HangupTimeout = self.xml.get_widget(\
            "hangupTimeoutISDNSB").get_value_as_int()
        dialup.DialMode = self.xml.get_widget("dialModeISDNEntry").get_text()
        if dialup.DialMode == DialModes[DM_AUTO]:
            dialup.DialMode = DM_AUTO
            dialup.DefRoute = TRUE
        else:
            dialup.DialMode = DM_MANUAL
            dialup.DefRoute = FALSE

        dialup.MSN = self.xml.get_widget("msnEntry").get_text()

        dialup.ChannelBundling = self.xml.get_widget(\
            "channelBundlingCB").get_active()
        if dialup.ChannelBundling:
            dialup.SlaveDevice = getNewDialupDevice(\
                getDeviceList(), self.device)
        else:
            dialup.SlaveDevice = None
        dialup.DefRoute = self.xml.get_widget("defrouteISDNCB").get_active()

        auth = self.xml.get_widget("authEntry").get_text()
        if auth == _('pap'):
            dialup.Authentication = '+pap -chap'
        elif auth == _('chap'):
            dialup.Authentication = '-pap +chap'
        elif auth == _('chap+pap'):
            dialup.Authentication = '+chap +pap'
        else:
            dialup.Authentication = 'noauth'

        
class ModemDialupDialog(DialupDialog):
    def __init__(self, device):
        DialupDialog.__init__(self, device)
        
        self.dialog.set_title(_("Modem Dialup Configuration"))
        page = self.noteBook.page_num(self.xml.get_widget ("isdnTab"))
        self.noteBook.get_nth_page(page).hide()        
        page = self.noteBook.page_num(self.xml.get_widget ("callbackTab"))
        self.noteBook.get_nth_page(page).hide()
        
    def on_chooseButton_clicked(self, button):
        dialog = ModemproviderDialog(self.device)
        dl = dialog.xml.get_widget("Dialog")
        dl.set_transient_for(self.dialog)
        dl.run()
        dl.destroy()
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
            self.xml.get_widget("modemPortCombo").set_popdown_strings(\
                devicelist)

        dialup = self.device.Dialup
        if dialup.HangupTimeout:
            self.xml.get_widget("hangupTimeoutSB").set_value(\
                dialup.HangupTimeout)
        if dialup.DialMode:
            if dialup.DialMode == DM_AUTO:
                dialmode = DialModes[DM_AUTO]
            else:
                dialmode = DialModes[DM_MANUAL]
        else:
            dialmode = DialModes[DM_MANUAL]
        self.xml.get_widget("dialModeEntry").set_text(dialmode)

        if dialup.InitString:
           widget = self.xml.get_widget("modemInitEntry").set_text(\
               dialup.InitString)

        if dialup.Persist:
            self.xml.get_widget("persistCB").set_active(dialup.Persist)

        if dialup.DefRoute != None:
            self.xml.get_widget("defrouteCB").set_active(dialup.DefRoute)

        if dialup.Inherits:
            self.xml.get_widget("modemPortEntry").set_text(dialup.Inherits)

        self.xml.get_widget("stupidModeCB").set_active(\
            self.device.Dialup.StupidMode == true)

    def dehydrate(self):
        DialupDialog.dehydrate(self)
        dialup = self.device.Dialup
        dialup.HangupTimeout = self.xml.get_widget(\
                               "hangupTimeoutSB").get_value_as_int()
        dialup.DialMode = self.xml.get_widget("dialModeEntry").get_text()
        if dialup.DialMode == DialModes[DM_AUTO]: dialup.DialMode = DM_AUTO
        else: dialup.DialMode = DM_MANUAL
        dialup.InitString = self.xml.get_widget("modemInitEntry").get_text()
        self.device.Name = self.xml.get_widget('deviceNameEntry').get_text()
        dialup.Inherits = self.xml.get_widget("modemPortEntry").get_text()
        if not self.device.Device:
            self.device.Device = getNewDialupDevice(\
                getDeviceList(), self.device)
        dialup.Persist = self.xml.get_widget("persistCB").get_active()
        dialup.DefRoute = self.xml.get_widget("defrouteCB").get_active()
        dialup.StupidMode = self.xml.get_widget(\
            "stupidModeCB").get_active() == true


NCDevIsdn.setDevIsdnDialog(ISDNDialupDialog)
NCDevModem.setDevModemDialog(ModemDialupDialog)


# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = DialupDialog()
    window.run()
    gtk.mainloop()
