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

from provider import providerDialog
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
        
        glade_file = "dialupconfig.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = "/usr/share/netconf/" + glade_file

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
        #self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        #self.dialog.connect("hide", gtk.mainquit)
        self.load_icon("network.xpm")

        self.dialog.set_close(TRUE)


    def load_icon(self, pixmap_file, widget = None):
        if not os.path.exists(pixmap_file):
            pixmap_file = "pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "../pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "/usr/share/netconf/" + pixmap_file
        if not os.path.exists(pixmap_file):
            return

        pix, mask = gtk.create_pixmap_from_xpm(self.dialog, None, pixmap_file)
        gtk.GtkPixmap(pix, mask)

        if widget:
            widget.set(pix, mask)
        else:
            self.dialog.set_icon(pix, mask)

    def hydrate(self):
        # to be overloaded by specific dialup classes
        pass

    def dehydrate(self):
        # to be overloaded by specific dialup classes
        pass

    def on_Dialog_delete_event(self, *args):
        pass
    
    def on_okButton_clicked(self, button):
        self.dehydrate()
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
        self.xml.get_widget("ipppOptionList").set_sensitive(TRUE)
        self.xml.get_widget("ipppOptionList").append([entry.get_text()])
        entry.set_text("")
        entry.grab_focus()
    
    def on_pppOptionList_select_row(self, clist, r, c, event):
        self.xml.get_widget ("pppOptionDeleteButton").set_sensitive (TRUE)
    
    def on_ipppOptionList_unselect_row (self, clist, r, c, event):
        self.xml.get_widget("pppOptionDeleteButton").set_sensitive(FALSE)

    def on_pppOptionDeleteButton_clicked(self, button):
        clist = self.xml.get_widget("ipppOptionList")
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
        self.dialog.set_title("ISDN Dialup Configuration")
        
        self.dialog.show()

    def hydrate(self):
        # Fill in Dialog
        pass

    def dehydrate(self):
        # Fill in Device.Dialup class
        pass

class ModemDialupDialog(DialupDialog):
    def __init__(self, device, xml_main = None, xml_basic = None):
        DialupDialog.__init__(self, device, xml_main, xml_basic)
        
        self.dialog.set_title("Modem Dialup Configuration")
        for i in [1,5]:
            self.noteBook.get_nth_page(i).hide()
            
        self.dialog.show()

    def hydrate(self):
        # Fill in Dialog
        pass

    def dehydrate(self):
        # Fill in Device.Dialup class
        pass
        

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = DialupDialog()
    gtk.mainloop()

