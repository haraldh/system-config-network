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

from dialupconfig import dialupDialog
from ethernetconfig import ethernetConfigDialog
from dslconfig import dslConfigDialog
from editadress import editAdressDialog
from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class basicDialog:
    def __init__(self, xml = None):
        self.xml_main = xml
        self.xml = libglade.GladeXML("basicdialog.glade", None, domain="netconf")

        self.xml.signal_autoconnect(
            {
            "on_configureButton_clicked" : self.on_configureButton_clicked,
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_helpButton_clicked" : self.on_helpButton_clicked,
            "on_deviceNameEntry_changed" : self.on_deviceNameEntry_changed,
            "on_deviceNameEntry_insert_text" : (self.on_generic_entry_insert_text,
                                                r"^[a-z|A-Z|0-9]+$"),
            "on_ipSettingCB_toggled" : self.on_ipSettingCB_toggled,
            "on_defaultRouteCB_toggled" : self.on_defaultRouteCB_toggled,
            "on_routeAddButton_clicked" : self.on_routeAddButton_clicked,
            "on_routeEditButton_clicked" : self.on_routeEditButton_clicked,
            "on_routeDeleteButton_clicked" : self.on_routeDeleteButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.mainquit)
        pix, mask = gtk.create_pixmap_from_xpm(self.dialog, None,
                                               "pixmaps/network.xpm")
        gtk.GtkPixmap(pix, mask)
        self.dialog.set_icon(pix, mask)
        self.set_icon(self.xml.get_widget("networkPixmap"),
                      "pixmaps/network.xpm")
        self.dialog.show_all()

    def set_icon(self, widget, pixmapFile):
        if os.path.exists (pixmapFile):
            pix, mask = gtk.create_pixmap_from_xpm (gtk.GtkWindow (), None,
                                                    pixmapFile)
            widget.set (pix, mask)

    def on_Dialog_delete_event(self, *args):
        self.dialog.destroy()
        gtk.mainquit()

    def on_okButton_clicked(self, button):
        self.dialog.destroy()
        gtk.mainquit()

    def on_cancelButton_clicked(self, button):
        self.dialog.destroy()
        gtk.mainquit()

    def on_helpButton_clicked(self, button):
        pass

    def on_configureButton_clicked(self, button):
        deviceType = self.xml.get_widget("deviceTypeEntry").get_text()
        if deviceType == "Ethernet":
            ethernetConfigDialog(self.xml_main, self.xml)
            gtk.mainloop()
        elif deviceType == "ISDN":
            dialupDialog(self.xml_main, self.xml)
            gtk.mainloop()
        elif deviceType == "Modem":
            dialupDialog(self.xml_main, self.xml, "Modem")
            gtk.mainloop()
        elif deviceType == "xDSL":
            dslConfigDialog()
            gtk.mainloop()
        elif deviceType == "CIPE":
            print "CIPE configuration"
        elif deviceType == "Wireless":
            print "wireless configuration"

    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')
    
    def on_deviceNameEntry_changed(self, entry):
        deviceName = string.strip(entry.get_text())
        self.xml.get_widget("deviceTypeComboBox").set_sensitive(len(deviceName) > 0)
        self.xml.get_widget("configureButton").set_sensitive(len(deviceName) > 0)

    def on_ipSettingCB_toggled(self, check):
        self.xml.get_widget("dynamicConfigComboBox").set_sensitive(check["active"])
        self.xml.get_widget("ipSettingFrame").set_sensitive(check["active"] != TRUE)
        if check["active"]:
            self.xml.get_widget ("dynamicConfigEntry").grab_focus()
        else:
            self.xml.get_widget ("addressEntry").grab_focus()

    def on_defaultRouteCB_toggled(self, check):
        self.xml.get_widget("networkRouteFrame").set_sensitive(check["active"] != TRUE)

    def on_routeAddButton_clicked(self, button):
        editAdressDialog(self.xml_main, self.xml)

    def on_routeEditButton_clicked(self, button):
        editAdressDialog(self.xml_main, self.xml, list)

    def on_routeDeleteButton_clicked(self, button):
        pass

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = basicDialog()
    gtk.mainloop()

