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

import sys
import getopt
import signal
import os
import os.path
import GdkImlib
import string
import gettext

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

if not "/usr/share/netconf" in sys.path:
    sys.path.append("/usr/share/netconf")

import Conf

from netconfpkg import *

import gtk
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
        import GDK
        import GTK
        import libglade
        import gnome
        import gnome.ui

        glade_file = "maindialog.glade"

        if not os.path.isfile(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.isfile(glade_file):
            glade_file = "/usr/share/netconf/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")
        self.initialized = None

        self.xml.signal_autoconnect(
            {
            "on_deviceAddButton_clicked" : self.on_deviceAddButton_clicked,
            "on_deviceCopyButton_clicked" : self.on_deviceCopyButton_clicked,
            "on_deviceEditButton_clicked" : self.on_deviceEditButton_clicked,
            "on_deviceDeleteButton_clicked" : self.on_deviceDeleteButton_clicked,
            "on_deviceList_select_row" : (self.on_generic_clist_select_row,
                                          self.xml.get_widget("deviceEditButton"),
                                          self.xml.get_widget("deviceDeleteButton"),
                                          self.xml.get_widget("deviceCopyButton")),
            "on_deviceList_unselect_row" : (self.on_generic_clist_unselect_row,
                                            self.xml.get_widget("deviceEditButton"),
                                            self.xml.get_widget("deviceDeleteButton"),
                                            self.xml.get_widget("deviceCopyButton")),
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
            "on_hostnameEntry_changed" : self.on_hostnameEntry_changed,
            "on_domainEntry_changed" : self.on_domainEntry_changed,
            "on_primaryDnsEntry_changed" : self.on_primaryDnsEntry_changed,
            "on_secondaryDnsEntry_changed" : self.on_secondaryDnsEntry_changed,
            "on_ternaryDnsEntry_changed" : self.on_ternaryDnsEntry_changed,
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
            "on_hostsAddButton_clicked" : self.on_hostsAddButton_clicked,
            "on_hostsEditButton_clicked" : self.on_hostsEditButton_clicked,
            "on_hostsDeleteButton_clicked" : self.on_hostsDeleteButton_clicked,
            "on_profileList_unselect_row" : (self.on_generic_clist_unselect_row,
                                             self.xml.get_widget("profileEditButton"),
                                             self.xml.get_widget("profileDeleteButton"),
                                             self.xml.get_widget("profileCopyButton")),
            "on_profileList_select_row" : (self.on_generic_clist_select_row,
                                           self.xml.get_widget("profileEditButton"),
                                           self.xml.get_widget("profileDeleteButton"),
                                           self.xml.get_widget("profileCopyButton")),
            "on_profileList_button_press_event" : (self.on_generic_clist_button_press_event,
                                                   self.on_profileRenameButton_clicked),
            "on_profileAddButton_clicked" : self.on_profileAddButton_clicked,
            "on_profileCopyButton_clicked" : self.on_profileCopyButton_clicked,
            "on_profileRenameButton_clicked" : self.on_profileRenameButton_clicked,
            "on_profileDeleteButton_clicked" : self.on_profileDeleteButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.mainquit)
        self.load_icon("network.xpm")
        self.load()
        self.hydrate()

    def load(self):
        self.loadDevices()
        self.loadHardware()
        self.loadProfiles()

    def loadDevices(self):
        devicelist = getDeviceList()

    def loadHardware(self):
        hardwarelist = getHardwareList()

    def loadProfiles(self):
        profilelist = getProfileList()

    def save(self):
        self.saveDevices()
        self.saveHardware()
        self.saveProfiles()

    def saveDevices(self):
        devicelist = getDeviceList()
        devicelist.save()

    def saveHardware(self):
        hardwarelist = getHardwareList()
        hardwarelist.save()

    def saveProfiles(self):
        profilelist = getProfileList()
        profilelist.save()

    def hydrate(self):
        self.hydrateDevices()
        self.hydrateHardware()
        self.hydrateProfiles()

    def hydrateDevices(self):
        devicelist = getDeviceList()
        hardwarelist = getHardwareList()
        profilelist = getProfileList()

        clist = self.xml.get_widget("deviceList")
        clist.clear()
        act_xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "/usr/share/netconf/pixmaps/active.xpm")
        inact_xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "/usr/share/netconf/pixmaps/inactive.xpm")

        row = 0
        for dev in devicelist:
            type = dev.Type
            for i in xrange(len(hardwarelist)):
                if hardwarelist[i].Name == dev.Device:
                    type = hardwarelist[i].Type
            clist.append(['', dev.DeviceId, type])
            clist.set_pixmap(row, 0, inact_xpm)
            clist.set_row_data(row, 0)
            for prof in profilelist:
                if (prof.Active == true or prof.ProfileName == 'default') and dev.DeviceId in prof.ActiveDevices:
                    clist.set_pixmap(row, 0, act_xpm)
                    clist.set_row_data(row, 1)
            row = row + 1

    def hydrateHardware(self):
        hardwarelist = getHardwareList()

        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        hardwareTypeList = ["Ethernet", "Modem", "ISDN"]
        self.xml.get_widget("hardwareTypeCombo").set_popdown_strings(hardwareTypeList)
        for hw in hardwarelist:
            if hw.Type == "ISDN":
                hardwareTypeList = ["Ethernet", "Modem"]
                self.xml.get_widget("hardwareTypeCombo").set_popdown_strings(hardwareTypeList)
            clist.append([hw.Description, hw.Type, hw.Name])

    def hydrateProfiles(self):
        profilelist = getProfileList()

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
                    hclist.append([host.IP, host.Hostname, string.join(host.AliasList, ' ')])

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
        if not os.path.isfile(pixmap_file):
            pixmap_file = "pixmaps/" + pixmap_file
        if not os.path.isfile(pixmap_file):
            pixmap_file = "../pixmaps/" + pixmap_file
        if not os.path.isfile(pixmap_file):
            pixmap_file = "/usr/share/netconf/" + pixmap_file
        if not os.path.isfile(pixmap_file):
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
        profilelist = getProfileList()
        devicelist = getDeviceList()

        clist = self.xml.get_widget("deviceList")

        for i in xrange (clist.rows):
            type = clist.get_text (i, 1)
            if type == 'default':
                continue
            elif type == 'URL':
                value = clist.get_text (i, 2)
            else:
                value = 'file:' + clist.get_text (i, 2)

        device = Device()

        basic = basicDialog(device, self.xml)
        basic.xml.get_widget ("okButton").set_sensitive(FALSE)
        dialog = basic.xml.get_widget ("Dialog")
        button = dialog.run ()
        if button == 0:
            i = devicelist.addDevice()
            devicelist[i].apply(device)
            devicelist[i].commit()
            for prof in profilelist:
                if prof.Active == false:
                    continue
                prof.ActiveDevices.append(device.DeviceId)
            self.hydrate()

    def on_deviceCopyButton_clicked (self, button):
        devicelist = getDeviceList()

        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        device = Device()
        device.apply(devicelist[clist.selection[0]])
        device.DeviceId = device.DeviceId + 'Copy'
        i = devicelist.addDevice()
        devicelist[i].apply(device)
        devicelist[i].commit()
        self.hydrate()

    def on_deviceEditButton_clicked (self, *args):
        devicelist = getDeviceList()

        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        device = devicelist[clist.selection[0]]

        name = clist.get_text(clist.selection[0], 1)
        type = clist.get_text(clist.selection[0], 2)

        if type == 'Loopback':
            generic_error_dialog ('The Loopback device can not be edited!', self.xml.get_widget ("Dialog"))
            return

        basic = basicDialog(device, self.xml)
        dialog = basic.xml.get_widget ("Dialog")
        dialog.set_title ("Edit Device")
        button = dialog.run ()
        self.hydrate()

    def on_deviceDeleteButton_clicked (self, button):
        devicelist = getDeviceList()
        profilelist = getProfileList()

        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        device = devicelist[clist.selection[0]]

        name = clist.get_text(clist.selection[0], 1)
        type = clist.get_text(clist.selection[0], 2)

        if type == 'Loopback':
            generic_error_dialog ('The Loopback device can not be removed!', self.xml.get_widget ("Dialog"))
            return

        for prof in profilelist:
            if name in prof.ActiveDevices:
                pos = prof.ActiveDevices.index(name)
                del prof.ActiveDevices[pos]

        del devicelist[clist.selection[0]]
        self.hydrate()

    def on_generic_entry_insert_text(self, entry, partial_text, length, pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_generic_clist_select_row(self, clist, row, column, event,
                                    edit_button = None, delete_button = None,
                                    copy_button = None, rename_button = None,
                                    up_button = None, down_button = None):
        profilelist = getProfileList()
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
            self.hydrate()

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
        profilelist = getProfileList()

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
                name = clist.get_text(row, 1)
                type = clist.get_text(row, 2)
                if type == 'Loopback':
                    generic_error_dialog ('The Loopback device can not be disabled!', self.xml.get_widget ("Dialog"))
                    return

                if clist.get_row_data(row) == 0:
                    xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "pixmaps/active.xpm")
                    clist.set_row_data(row, 1)
                    curr_prof = profilelist[self.xml.get_widget('profileList').selection[0]]
                    if curr_prof.ProfileName == 'default':
                        for prof in profilelist:
                            activateDevice(name, prof.ProfileName, true)
                    else:
                        activateDevice(name, curr_prof.ProfileName, true)
                else:
                    xpm, mask = gtk.create_pixmap_from_xpm(self.dialog, None, "pixmaps/inactive.xpm")
                    clist.set_row_data(row, 0)
                    curr_prof = profilelist[self.xml.get_widget('profileList').selection[0]]
                    if curr_prof.ProfileName == 'default':
                        for prof in profilelist:
                            activateDevice(name, prof.ProfileName, false)
                    else:
                        activateDevice(name, curr_prof.ProfileName, false)
#                        activateDevice(name, 'default', false)
                clist.set_pixmap(row, 0, xpm)

    def on_hostnameEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.Hostname = entry.get_text()

    def on_domainEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.Domainname = entry.get_text()

    def on_primaryDnsEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.PrimaryDNS = entry.get_text()

    def on_secondaryDnsEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.SecondaryDNS = entry.get_text()

    def on_ternaryDnsEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.TernaryDNS = entry.get_text()

    def on_searchDnsEntry_changed(self, entry):
        pass

    def on_dnsAddButton_clicked(self, *args):
        profilelist = getProfileList()

        searchDnsEntry = self.xml.get_widget("searchDnsEntry").get_text()
        self.xml.get_widget("searchDnsEntry").set_text("")
        if len(string.strip(searchDnsEntry)) == 0:
            return
        
        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.SearchList.append(searchDnsEntry)
                prof.DNS.SearchList.commit()
                self.hydrate()

    def on_dnsEditButton_clicked (self, *args):
        clist = self.xml.get_widget("dnsList")
        name = clist.get_text(clist.selection[0], 0)
        if len(clist.selection) == 0:
            return
        
        dialog = editDomainDialog(name)
        dialog.main = self
        dialog.xml.get_widget("Dialog").run()
        
    def on_dnsUpButton_clicked (self, button):
        profilelist = getProfileList()

        clist = self.xml.get_widget("dnsList")
        name = clist.get_text(clist.selection[0], 0)

        if len(clist.selection) == 0 or clist.selection == 0:
            return

        for prof in profilelist:
            if prof.Active == true:
                index = prof.DNS.SearchList.index(name)
                if index == 0:
                    return
                
                n = prof.DNS.SearchList[index-1]
                prof.DNS.SearchList[index-1] = name
                prof.DNS.SearchList[index] = n
                prof.DNS.SearchList.commit()
                self.hydrate()
                clist.select_row(index-1, 0)

    def on_dnsDownButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget("dnsList")
        name = clist.get_text(clist.selection[0], 0)

        if len(clist.selection) == 0 or clist.selection == 0:
            return

        for prof in profilelist:
            if prof.Active == true:
                index = prof.DNS.SearchList.index(name)
                if len(prof.DNS.SearchList) == index + 1:
                    return
                
                n = prof.DNS.SearchList[index+1]
                prof.DNS.SearchList[index+1] = name
                prof.DNS.SearchList[index] = n
                prof.DNS.SearchList.commit()
                self.hydrate()
                clist.select_row(index+1, 0)

    def on_dnsDeleteButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget("dnsList")
        if len(clist.selection) == 0:
            return
        
        for prof in profilelist:
            if prof.Active == true:
                del prof.DNS.SearchList[clist.selection[0]]
                self.hydrate()

    def on_hostsAddButton_clicked(self, *args):
        profilelist = getProfileList()

        curr_prof = profilelist[self.xml.get_widget('profileList').selection[0]]
        if not curr_prof.HostsList:
            curr_prof.createHostsList()
        hostslist = curr_prof.HostsList
        host = Host()
        clist  = self.xml.get_widget("hostsList")
        dialog = editHostsDialog(host, self.xml)
        dl = dialog.xml.get_widget ("Dialog")
        button = dl.run ()
        if button == 0:
            i = hostslist.addHost()
            hostslist[i].apply(host)
            hostslist[i].commit()
        self.hydrate()

    def on_hostsEditButton_clicked (self, *args):
        profilelist = getProfileList()

        curr_prof = profilelist[self.xml.get_widget('profileList').selection[0]]
        hostslist = curr_prof.HostsList
        clist  = self.xml.get_widget("hostsList")

        if len(clist.selection) == 0:
            return

        host = hostslist[clist.selection[0]]

        dialog = editHostsDialog(host, self.xml)
        dl = dialog.xml.get_widget ("Dialog")
        dl.run ()
        self.hydrate()

    def on_hostsDeleteButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget('profileList')

        if len(clist.selection) == 0:
            return

        prof = profilelist[clist.selection[0]]

        clist = self.xml.get_widget('hostsList')

        if len(clist.selection) == 0:
            return

        del prof.HostsList[clist.selection[0]]
        self.hydrate()

    def on_profileList_click_column (self, *args):
        pass

    def on_profileList_select_row (self, *args):
        pass

    def on_profileAddButton_clicked (self, *args):
        import gnome
        import gnome.ui
        dialog = gnome.ui.GnomeRequestDialog (FALSE, "Please enter the name for the new profile.\nThe name may only contain letters and digits.", "NewProfile", 50, self.on_profileEntry_changed, self.dialog)
        dialog.run()

    def on_profileEntry_changed(self, text):
        profilelist = getProfileList()

        if not text or not re.match("^[a-z|A-Z|0-9]+$", text):
            return

        i = profilelist.addProfile()
        prof = profilelist[i]
        prof.createActiveDevices()
        prof.createDNS()
        prof.createHostsList()
        prof.ProfileName      = text
        prof.DNS.Hostname     = ''
        prof.DNS.Domainname   = ''
        prof.DNS.PrimaryDNS   = ''
        prof.DNS.SecondaryDNS = ''
        prof.DNS.TernaryDNS   = ''
        prof.DNS.createSearchList()
        self.xml.get_widget("profileList").clear()
        self.initialized = false
        self.hydrate()

    def on_profileCopyButton_clicked (self, *args):
        pass

    def on_profileRenameButton_clicked (self, *args):
        pass

    def on_profileDeleteButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget('profileList')

        if len(clist.selection) == 0:
            return

        if profilelist[clist.selection[0]].ProfileName == 'default':
            generic_error_dialog ('The default Profile can not be deleted!', self.xml.get_widget ("Dialog"))
            return
        del profilelist[clist.selection[0]]
        self.hydrate()

    def on_hardwareAddButton_clicked (self, *args):
        type = self.xml.get_widget('hardwareTypeEntry').get_text()
        self.showHardwareDialog(type, false)

    def on_hardwareEditButton_clicked (self, *args):
        clist = self.xml.get_widget('hardwareList')
        type  = clist.get_text(clist.selection[0], 1)
        self.showHardwareDialog(type, true)

    def showHardwareDialog(self, deviceType, edit):
        hardwarelist = getHardwareList()

        if deviceType == 'Ethernet' or deviceType == 'Token Ring' or  \
           deviceType == 'Pocket (ATP)' or deviceType == 'Arcnet':
            if not edit:
                i = hardwarelist.addHardware()
                hw = hardwarelist[i]
            else:
                clist = self.xml.get_widget('hardwareList')

                if len(clist.selection) == 0:
                    return

                hw = hardwarelist[clist.selection[0]]
            dialog = ethernetHardwareDialog(hw, self.xml)

        if deviceType == 'Modem':
            if edit:
                clist = self.xml.get_widget('hardwareList')
                type  = clist.get_text(clist.selection[0], 1)
                dev   = clist.get_text(clist.selection[0], 2)
                for hw in hardwarelist:
                    if hw.Name == dev:
                        break;
                dialog = editmodemDialog(hw.Name)
            else:
                dialog = addmodemDialog()

        if deviceType == 'ISDN':
            if edit:
                clist = self.xml.get_widget('hardwareList')
                Description = clist.get_text(clist.selection[0], 0)
                type  = clist.get_text(clist.selection[0], 1)
                dev   = clist.get_text(clist.selection[0], 2)
                for hw in hardwarelist:
                    if hw.Description == Description:
                        break;
                dialog = editisdnHardwareDialog(hw.Description)
            else:
                dialog = addisdnHardwareDialog()
                
        button = dialog.xml.get_widget('Dialog').run()
        if button == 0:
            hardwarelist.commit()
        else:
            hardwarelist.rollback()
        self.hydrate()
            
    def on_hardwareDeleteButton_clicked (self, *args):
        hardwarelist = getHardwareList()

        clist = self.xml.get_widget("hardwareList")

        if len(clist.selection) == 0:
            return

        hw = hardwarelist[clist.selection[0]]
        description = clist.get_text(clist.selection[0], 0)
        type = clist.get_text(clist.selection[0], 1)
        dev = clist.get_text(clist.selection[0], 2)

        del hardwarelist[clist.selection[0]]
        hardwarelist.commit()
        self.hydrate()


# make ctrl-C work
if __name__ == '__main__':
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    class BadUsage: pass

    updateNetworkScripts()

    if sys.argv[0][-11:] != 'netconf-cmd':
        window = mainDialog()
        gtk.mainloop()
        sys.exit(0)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:t", ["profile=", "test"])
        for opt, val in opts:
            if opt == '-p' or opt == '--profile':
                switchToProfile(val)
                continue

            if opt == '-t' or opt == '--test':
                print "Just a test for getopt"
                continue

            raise BadUsage

        for arg in args:
            print args

    except (getopt.error, BadUsage):
        print """netconf-cmd - Python network configuration commandline tool

Usage: netconf-cmd [-p --profile <profile>]"""
