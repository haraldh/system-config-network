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
import Conf

from netconfpkg import *
from Resolver import ResolverFile

from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class mainDialog:
    deviceTypes = {'eth[0-9]+(:[0-9]+)?':'Ethernet',
                   'lo':'Loopback'}

    def __init__(self):
        glade_file = "maindialog.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = "/usr/share/netconf/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")
        

        self.xml.signal_autoconnect(
            {
            "on_deviceAddButton_clicked" : self.on_deviceAddButton_clicked,
            "on_deviceCopyButton_clicked" : self.on_deviceCopyButton_clicked,
            "on_deviceRenameButton_clicked" : self.on_deviceRenameButton_clicked,
            "on_deviceEditButton_clicked" : self.on_deviceEditButton_clicked,
            "on_deviceDeleteButton_clicked" : self.on_deviceDeleteButton_clicked,
            "on_deviceList_select_row" : (self.on_generic_clist_select_row,
                                          self.xml.get_widget("deviceEditButton"),
                                          self.xml.get_widget("deviceDeleteButton"),
                                          self.xml.get_widget("deviceCopyButton"),
                                          self.xml.get_widget("deviceRenameButton")),
            "on_deviceList_unselect_row" : (self.on_generic_clist_unselect_row,
                                            self.xml.get_widget("deviceEditButton"),
                                            self.xml.get_widget("deviceDeleteButton"),
                                            self.xml.get_widget("deviceCopyButton"),
                                            self.xml.get_widget("deviceRenameButton")),
            "on_deviceList_button_press_event" : (self.on_generic_clist_button_press_event,
                                                  self.on_deviceEditButton_clicked),
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_helpButton_clicked" : self.on_helpButton_clicked,
            "on_hardwareAddButton_clicked" : self.on_hardwareAddButton_clicked,
            "on_hardwareEditButton_clicked" : self.on_hardwareEditButton_clicked,
            "on_hardwareDeleteButton_clicked" : self.on_hardwareDeleteButton_clicked,
            "on_hardwareList_select_row" : (self.on_generic_clist_select_row,
                                            self.xml.get_widget("hardwareEditButton"),
                                            self.xml.get_widget("hardwareDeleteButton")),
            "on_hardwareList_unselect_row" : (self.on_generic_clist_unselect_row,
                                              self.xml.get_widget("hardwareEditButton"),
                                              self.xml.get_widget("hardwareDeleteButton")),
            "on_hardwareList_button_press_event" : (self.on_generic_clist_button_press_event,
                                                    self.on_hardwareEditButton_clicked),
            "on_primaryDnsEntry_changed" : (self.on_generic_entry_insert_text, r'^[^/ ]+$'),
            "on_secondaryDnsEntry_changed" : (self.on_generic_entry_insert_text,  r'^[^/ ]+$'),
            "on_ternaryDnsEntry_changed" : (self.on_generic_entry_insert_text,  r'^[^/ ]+$'),
            "on_searchDnsEntry_changed" : self.on_searchDnsEntry_changed,
            "on_dnsAddButton_clicked" : self.on_dnsAddButton_clicked,
            "on_dnsEditButton_clicked" : self.on_dnsEditButton_clicked,
            "on_dnsUpButton_clicked" : self.on_dnsUpButton_clicked,
            "on_dnsDownButton_clicked" : self.on_dnsDownButton_clicked,
            "on_dnsDeleteButton_clicked" : self.on_dnsDeleteButton_clicked,
            "on_dnsList_select_row" : (self.on_generic_clist_select_row,
                                       self.xml.get_widget("dnsEditButton"),
                                       self.xml.get_widget("dnsDeleteButton"),
                                       None, None,
                                       self.xml.get_widget("dnsUpButton"),
                                       self.xml.get_widget("dnsDownButton")),
            "on_dnsList_unselect_row" : (self.on_generic_clist_unselect_row,
                                         self.xml.get_widget("dnsEditButton"),
                                         self.xml.get_widget("dnsDeleteButton"),
                                         None, None,
                                         self.xml.get_widget("dnsUpButton"),
                                         self.xml.get_widget("dnsDownButton")),
            "on_dnsList_button_press_event" : (self.on_generic_clist_button_press_event,
                                               self.on_dnsEditButton_clicked),
            "on_profileList_unselect_row" : (self.on_generic_clist_unselect_row,
                                             self.xml.get_widget("profileEditButton"),
                                             self.xml.get_widget("profileDeleteButton"),
                                             self.xml.get_widget("profileCopyButton")),
            "on_profileList_select_row" : (self.on_generic_clist_select_row,
                                           self.xml.get_widget("profileEditButton"),
                                           self.xml.get_widget("profileDeleteButton"),
                                           self.xml.get_widget("profileCopyButton")),
            "on_profileList_button_press_event" : (self.on_generic_clist_button_press_event,
                                                   self.on_profileDeleteButton_clicked),
            "on_profileAddButton_clicked" : self.on_profileAddButton_clicked,
            "on_profileCopyButton_clicked" : self.on_profileCopyButton_clicked,
            "on_profileDeleteButton_clicked" : self.on_profileDeleteButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.mainquit)
        self.load_icon("network.xpm")
	self.load()

    def load(self):
        self.loadDevices()
        self.loadDNS()

    def loadDevices(self):
        devices = filter(lambda x: x[:6] == 'ifcfg-', os.listdir("/etc/sysconfig/networking/devices/"))
        clist = self.xml.get_widget("deviceList")
	act_xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "pixmaps/active.xpm")
	inact_xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "pixmaps/inactive.xpm")

        nwconf = Conf.ConfShellVar("/etc/sysconfig/network")

        row = 0
        for i in devices:
            devconf = Conf.ConfShellVar("/etc/sysconfig/networking/devices/" + i)
            dev = devconf['DEVICE']
            type = 'Unknown'
            for j in self.deviceTypes.keys():
                if re.search(j, dev):
                    type = self.deviceTypes[j]

            clist.append(['', i[6:], type])

            if not nwconf['CURRENT_PROFILE'] or not os.path.exists("/etc/sysconfig/networking/profiles/"+ nwconf['CURRENT_PROFILE'] + "/" + i):
                clist.set_pixmap(row, 0, inact_xpm)
            else:
                clist.set_pixmap(row, 0, act_xpm)
            row = row + 1

    def loadDNS(self):
        res_file = ResolverFile()
        try:
            res_file.readProfile()
            dns = res_file.DNServers()
            search_domain = res_file.searchDomains()
            n = ["primaryDnsEntry", "secondaryDnsEntry", "ternaryDnsEntry"]
            for i in range(len(dns)):
                self.xml.get_widget(n[i]).set_text(dns[i])
            for i in range(len(search_domain)):
                self.xml.get_widget("dnsList").append([search_domain[i]])
        except:
            pass

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
        gtk.mainquit()

    def on_okButton_clicked (self, button):
        gtk.mainquit()

    def on_cancelButton_clicked(self, button):
        gtk.mainquit()

    def on_helpButton_clicked(self, button):
        pass

    def on_deviceAddButton_clicked (self, clicked):
        clist = self.xml.get_widget("deviceList")

        for i in xrange (clist.rows):
            type = clist.get_text (i, 1)
            if type == 'default':
                continue
            elif type == 'URL':
                value = clist.get_text (i, 2)
            else:
                value = 'file:' + clist.get_text (i, 2)

        basic = basicDialog(self.xml)
        dialog = basic.xml.get_widget ("Dialog")
        dialog.show ()
#        gtk.mainloop()

    def on_deviceCopyButton_clicked (self, button):
        pass

    def on_deviceRenameButton_clicked (self, button):
        pass

    def on_deviceEditButton_clicked (self, *args):
        basic = basicDialog(self.xml)
        dialog = basic.xml.get_widget ("Dialog")
        dialog.set_title ("Edit Device")
        dialog.show ()

    def on_deviceDeleteButton_clicked (self, button):
        pass

    def on_generic_entry_insert_text(self, entry, partial_text, length, pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_generic_clist_select_row(self, clist, row, column, event,
                                    edit_button = None, delete_button = None,
                                    copy_button = None, rename_button = None,
                                    up_button = None, down_button = None):
        if edit_button: edit_button.set_sensitive(TRUE)
        if rename_button: rename_button.set_sensitive(TRUE)
        if delete_button: delete_button.set_sensitive(TRUE)
        if copy_button: copy_button.set_sensitive(TRUE)
        if up_button: delete_button.set_sensitive(TRUE)
        if down_button: copy_button.set_sensitive(TRUE)
        
    def on_generic_clist_unselect_row(self, clist, row, column, event,
                                      edit_button = None, delete_button = None,
                                      copy_button = None, rename_button = None,
                                      up_button = None, down_button = None):
        if edit_button: edit_button.set_sensitive(FALSE)
        if rename_button: rename_button.set_sensitive(FALSE)
        if delete_button: delete_button.set_sensitive(FALSE)
        if copy_button: copy_button.set_sensitive(FALSE)
        if up_button: delete_button.set_sensitive(FALSE)
        if down_button: copy_button.set_sensitive(FALSE)

    def on_generic_clist_button_release_event(self, clist, event, func):
        id = clist.get_data ("signal_id")
        clist.disconnect (id)
        clist.remove_data ("signal_id")
        apply (func)

    def on_generic_clist_button_press_event(self, clist, event, func):
        if event.type == GDK._2BUTTON_PRESS:
            info = clist.get_selection_info(event.x, event.y)
            if info != None:
                id = clist.signal_connect("button_release_event",
                                          self.on_generic_clist_button_release_event,
                                          func)
                clist.set_data("signal_id", id)

    def on_searchDnsEntry_changed(self, entry):
        pass

    def on_dnsAddButton_clicked(self, *args):
        pass

    def on_dnsEditButton_clicked (self, *args):
        pass

    def on_dnsUpButton_clicked (self, *args):
        pass

    def on_dnsDownButton_clicked (self, *args):
        pass

    def on_dnsDeleteButton_clicked (self, *args):
        pass

    def on_profileList_click_column (self, *args):
        pass

    def on_profileList_select_row (self, *args):
        pass

    def on_profileAddButton_clicked (self, *args):
        pass

    def on_profileCopyButton_clicked (self, *args):
        pass

    def on_profileDeleteButton_clicked (self, *args):
        pass

    def on_hardwareAddButton_clicked (self, button):
        deviceType = self.xml.get_widget("deviceTypeEntry").get_text()
        if deviceType == "Ethernet" or deviceType == "Token Ring" or  \
           deviceType == "Pocket (ATP)" or deviceType == "Arcnet":
            dialog = ethernetHardwareDialog(self.xml)
        if deviceType == "Modem":
            dialog = modemDialog(self.xml)
        if deviceType == "ISDN":
            dialog = isdnHardwareDialog(self.xml)

    def on_hardwareEditButton_clicked (self, button):
        on_hardwareAddButton_clicked (button)

    def on_hardwareDeleteButton_clicked (self, button):
        pass

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = mainDialog()
    gtk.mainloop()

