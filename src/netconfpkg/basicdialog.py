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

from dialupconfig import *
from ethernetconfig import ethernetConfigDialog
from dslconfig import dslConfigDialog
from editadress import editAdressDialog
from NC_functions import *
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
    def __init__(self, device, xml = None):
        self.xml_main = xml
        self.device = device
        glade_file = "basicdialog.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = "/usr/share/netconf/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")
        self.xml.signal_autoconnect(
            {
            "on_configureButton_clicked" : self.on_configureButton_clicked,
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_applyButton_clicked" : self.on_applyButton_clicked,
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
        self.load_icon("network.xpm")
        self.load_icon("network.xpm", self.xml.get_widget("networkPixmap"))

        notebook = self.xml.get_widget("basicNotebook")

        self.xml.get_widget('deviceTypeComboBox').set_popdown_strings(deviceTypes)
        self.hydrate()

        self.xml.get_widget("okButton").set_sensitive(len(self.xml.get_widget('deviceNameEntry').get_text()) > 0)

        for wname in [ "trafficFrame", "securityFrame", "accountingFrame" ]:
            widget = self.xml.get_widget (wname)
            if widget:
                page = notebook.page_num(widget)
                if page:                
                    notebook.remove_page(page)

        self.dialog.set_close(TRUE)
        #self.dialog.close_hides(TRUE)
        #self.dialog.show()

    def hydrate(self):
        if self.device.DeviceId:
            self.xml.get_widget('deviceNameEntry').set_text(self.device.DeviceId)
            if self.device.Type and self.device.Type != "" \
               and self.device.Type != "Unknown":
                self.xml.get_widget('deviceTypeEntry').set_text(str(self.device.Type))
                self.xml.get_widget("deviceTypeComboBox").set_sensitive(FALSE)
                
            self.xml.get_widget('onBootCB').set_active(self.device.OnBoot)
            self.xml.get_widget('userControlCB').set_active(self.device.AllowUser)

            if self.device.BootProto == "static":
                self.xml.get_widget('ipSettingCB').set_active(FALSE)
                if self.device.IP:
                    self.xml.get_widget('addressEntry').set_text(self.device.IP)
                if self.device.Netmask:
                    self.xml.get_widget('netmaskEntry').set_text(self.device.Netmask)
                if self.device.Gateway:
                    self.xml.get_widget('gatewayEntry').set_text(self.device.Gateway)
            else:
                self.xml.get_widget('ipSettingCB').set_active(TRUE)
                if self.device.Type == "ISDN" or self.device.Type == "Modem" or \
                   self.device.Type == "xDSL":
                    self.xml.get_widget("dynamicConfigEntry").set_text("DIALUP")

            if self.device.Hostname:
                self.xml.get_widget('hostnameEntry').set_text(self.device.Hostname)
            if self.device.AutoDNS:
                self.xml.get_widget('dnsSettingCB').set_active(self.device.AutoDNS)

    def dehydrate(self):
        self.device.DeviceId = self.xml.get_widget('deviceNameEntry').get_text()
        self.device.Type = self.xml.get_widget('deviceTypeEntry').get_text()
        self.device.OnBoot = self.xml.get_widget('onBootCB').get_active()
        self.device.AllowUser = self.xml.get_widget('userControlCB').get_active()
            
        if self.xml.get_widget('ipSettingCB').get_active(): 
            self.device.BootProto = self.xml.get_widget('dynamicConfigEntry').get_text()            
            self.device.IP = ''
            self.device.Netmask = ''
            self.device.Gateway = ''
        else:
            self.device.BootProto = 'static'
            self.device.IP = self.xml.get_widget('addressEntry').get_text()
            self.device.Netmask = self.xml.get_widget('netmaskEntry').get_text()
            self.device.Gateway = self.xml.get_widget('gatewayEntry').get_text()

        self.device.Hostname = self.xml.get_widget('hostnameEntry').get_text()
        self.device.AutoDNS = self.xml.get_widget('dnsSettingCB').get_active()

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
        
    def on_Dialog_delete_event(self, *args):
        self.device.rollback()
    
    def on_okButton_clicked(self, button):
        self.dehydrate()
        self.device.commit()
    
    def on_cancelButton_clicked(self, button):
        self.device.rollback()
    
    def on_applyButton_clicked(self, button):
        self.dehydrate()
        self.device.commit()

    def on_configureButton_clicked(self, button):
        deviceType = self.xml.get_widget("deviceTypeEntry").get_text()
        self.device.Type = deviceType
        if deviceType == "Ethernet":
            cfg = ethernetConfigDialog(self.device, self.xml_main, self.xml)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()
            self.on_deviceNameEntry_changed(self.xml.get_widget("deviceNameEntry"))
        elif deviceType == "ISDN":
            cfg = ISDNDialupDialog(self.device, self.xml_main, self.xml)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()
        elif deviceType == "Modem":
            cfg = ModemDialupDialog(self.device, self.xml_main, self.xml)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()
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
        self.device.DeviceId = deviceName
        self.xml.get_widget("deviceTypeComboBox").set_sensitive(len(deviceName) > 0)
        self.xml.get_widget("configureButton").set_sensitive(len(deviceName) > 0)
        self.xml.get_widget("okButton").set_sensitive(len(deviceName) > 0 and self.device.Device != None)

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

