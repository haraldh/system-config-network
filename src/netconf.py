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
    def __init__(self):
        glade_file = "maindialog.glade"

        if not isfile(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not isfile(glade_file):
            glade_file = "/usr/share/netconf/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")
        self.initialized = None

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
        self.setup()

    def load(self):
        self.loadDevices()
        self.loadHardware()
        self.loadProfiles()

    def loadDevices(self):
        global devicelist
        devicelist = DeviceList()
        devicelist.load()

    def loadHardware(self):
        global hardwarelist
        hardwarelist = HardwareList()
        hardwarelist.load()

    def loadProfiles(self):
        global profilelist
        profilelist = ProfileList()
        profilelist.load()

    def save(self):
        self.saveDevices()
        self.saveHardware()
        self.saveProfiles()

    def saveDevices(self):
        global devicelist
        devicelist.save()

    def saveHardware(self):
        global hardwarelist
        hardwarelist.save()

    def saveProfiles(self):
        global profilelist
        profilelist.save()

    def setup(self):
        self.setupDevices()
        self.setupHardware()
        self.setupProfiles()

    def setupDevices(self):
        global devicelist, profilelist

        clist = self.xml.get_widget("deviceList")
        clist.clear()
        act_xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "pixmaps/active.xpm")
        inact_xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "pixmaps/inactive.xpm")

        row = 0
        for dev in devicelist:
            type = getDeviceType(dev.Device)
            clist.append(['', dev.DeviceId, type])
            clist.set_pixmap(row, 0, inact_xpm)
            clist.set_row_data(row, 0)
            for prof in profilelist:
                if (prof.Active == true or prof.ProfileName == 'default') and dev.DeviceId in prof.ActiveDevices:
                    clist.set_pixmap(row, 0, act_xpm)
                    clist.set_row_data(row, 1)
            row = row + 1

    def setupHardware(self):
        global hardwarelist

        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        for hw in hardwarelist:
            if hw.Type == 'Modem':
                devname = hw.Modem.DeviceName
            else:
                devname = hw.Card.DeviceName
            clist.append([hw.Description, hw.Type, devname])

    def setupProfiles(self):
        global profilelist
        dclist = self.xml.get_widget("dnsList")
        dclist.clear()
        hclist = self.xml.get_widget("hostsList")
        hclist.clear()
        for prof in profilelist:
            if prof.Active == true:
                self.xml.get_widget('hostnameEntry').set_text(prof.DNS.Hostname)
                self.xml.get_widget('domainnameEntry').set_text(prof.DNS.Domainname)
                self.xml.get_widget('primaryDnsEntry').set_text(prof.DNS.PrimaryDNS)
                self.xml.get_widget('secondaryDnsEntry').set_text(prof.DNS.SecondaryDNS)
                self.xml.get_widget('ternaryDnsEntry').set_text(prof.DNS.TernaryDNS)
                for domain in prof.DNS.SearchList:
                    dclist.append([domain])

                for host in prof.HostsList:
                    al = ''
                    for alias in host.AliasList:
                        al = al + " " + alias
                    hclist.append([host.IP, host.Hostname, al])

        if self.initialized:
            return

        row = 0
        clist = self.xml.get_widget("profileList")
        self.initialized = true
        for prof in profilelist:
            clist.append([prof.ProfileName])
            if prof.Active == true:
                clist.select_row(row, 0)
            row = row + 1

    def load_icon(self, pixmap_file, widget = None):
        if not isfile(pixmap_file):
            pixmap_file = "pixmaps/" + pixmap_file
        if not isfile(pixmap_file):
            pixmap_file = "../pixmaps/" + pixmap_file
        if not isfile(pixmap_file):
            pixmap_file = "/usr/share/netconf/" + pixmap_file
        if not isfile(pixmap_file):
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
        self.save()
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

    def on_deviceCopyButton_clicked (self, button):
        pass

    def on_deviceRenameButton_clicked (self, button):
        pass

    def on_deviceEditButton_clicked (self, *args):
        global devicelist

        clist = self.xml.get_widget("deviceList")

        device = devicelist[clist.selection[0]]

        name = clist.get_text(clist.selection[0], 1)
        type = clist.get_text(clist.selection[0], 2)

        if type == 'Loopback':
            generic_error_dialog ('The Loopback device can not be edited!', self.xml.get_widget ("Dialog"))
            return

        basic = basicDialog(self.xml)
        basic.xml.get_widget('deviceNameEntry').set_text(name)
        basic.xml.get_widget('deviceNameEntry').set_editable(false)
        basic.xml.get_widget('deviceTypeEntry').set_text(type)
        basic.xml.get_widget('onBootCB').set_active(device.OnBoot)
        basic.xml.get_widget('userControlCB').set_active(device.AllowUser)

        basic.xml.get_widget('ipSettingCB').set_active(device.BootProto != 'static')
        if device.BootProto == 'static':
            basic.xml.get_widget('addressEntry').set_text(device.IP)
            basic.xml.get_widget('netmaskEntry').set_text(device.Netmask)
            basic.xml.get_widget('gatewayEntry').set_text(device.Gateway)

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
        if clist.get_name() == 'profileList':
            for prof in profilelist:
                prof.Active = false
            profilelist[row].Active = true
            self.setup()

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
        if clist.get_name() == 'deviceList' and event.type == GDK.BUTTON_PRESS:
            info = clist.get_selection_info(event.x, event.y)
            if info != None and info[1] == 0:
                row = info[0]
                if clist.get_row_data(row) == 0:
                    xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "pixmaps/active.xpm")
                    clist.set_row_data(row, 1)
                else:
                    xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "pixmaps/inactive.xpm")
                    clist.set_row_data(row, 0)
                clist.set_pixmap(row, 0, xpm)
                
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
