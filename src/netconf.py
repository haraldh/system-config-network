#! /usr/bin/python

## netconf - A network configuration tool
## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Than Ngo <than@redhat.com>
## Copyright (C) 2001 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001 Philipp Knirsch <pknirsch@redhat.com>
## Copyright (C) 2001 Trond Eivind Glomsrød <teg@redhat.com>

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

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

if not "/usr/share/redhat-config-network" in sys.path:
    sys.path.append("/usr/share/redhat-config-network")

if not "/usr/share/redhat-config-network/netconfpkg/" in sys.path:
    sys.path.append("/usr/share/redhat-config-network/netconfpkg")

# Workaround for buggy gtk/gnome commandline parsing python bindings.
cmdline = sys.argv[1:]
sys.argv = sys.argv[:1]

import getopt
import signal
import os
import os.path
import string
import gettext
import Conf

from netconfpkg import *

def Usage():
    print ( "redhat-config-network-cmd - Python network configuration commandline tool\n\nUsage: redhat-config-network-cmd -p --profile <profile>")


# Argh, another workaround for broken gtk/gnome imports...
if __name__ == '__main__':
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    class BadUsage: pass

    updateNetworkScripts()

    if sys.argv[0][-4:] == '-cmd':
        progname = os.path.basename(sys.argv[0])

        try:
            opts, args = getopt.getopt(cmdline, "p:th", ["profile=", "test", "help"])
            for opt, val in opts:
                if opt == '-p' or opt == '--profile':
                    profilelist = getProfileList()
                    profilelist.switchToProfile(val)
                    sys.exit(0)

                if opt == '-h' or opt == '--help':
                    Usage()
                    sys.exit(0)

                if opt == '-t' or opt == '--test':
                    print "Just a test for getopt"
                    sys.exit(0)

            raise BadUsage

        except (getopt.error, BadUsage):
            Usage()
            sys.exit(1)

import GdkImlib
import GDK
import GTK
import gtk
import libglade
import gnome
import gnome.ui
import gnome.help
from gtk import TRUE
from gtk import FALSE

##
## I18N
##
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
_=gettext.gettext

class mainDialog:
    def __init__(self):
        glade_file = "maindialog.glade"

        if not os.path.isfile(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain=PROGNAME)
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
            "on_tertiaryDnsEntry_changed" : self.on_tertiaryDnsEntry_changed,
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
        load_icon("network.xpm", self.dialog)
        self.load()
        self.hydrate()

    def load(self):
        self.loadDevices()
        self.loadHardware()
        self.loadProfiles()

    def loadDevices(self):
        devicelist = getDeviceList()
        devicelist.commit()

    def loadHardware(self):
        hardwarelist = getHardwareList()
        hardwarelist.commit()

    def loadProfiles(self):
        profilelist = getProfileList()
        profilelist.commit()

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
        profilelist = getProfileList()

        clist = self.xml.get_widget("deviceList")
        clist.clear()
        act_xpm, mask = get_icon ("pixmaps/active.xpm", self.dialog)
        inact_xpm, mask = get_icon ("pixmaps/inactive.xpm", self.dialog)

        row = 0
        for dev in devicelist:
            type = dev.Type
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
                if prof.DNS.Hostname: self.xml.get_widget('hostnameEntry').set_text(prof.DNS.Hostname)
                if prof.DNS.Domainname: self.xml.get_widget('domainnameEntry').set_text(prof.DNS.Domainname)
                if prof.DNS.PrimaryDNS: self.xml.get_widget('primaryDnsEntry').set_text(prof.DNS.PrimaryDNS)
                if prof.DNS.SecondaryDNS: self.xml.get_widget('secondaryDnsEntry').set_text(prof.DNS.SecondaryDNS)
                if prof.DNS.TertiaryDNS: self.xml.get_widget('tertiaryDnsEntry').set_text(prof.DNS.TertiaryDNS)
                for domain in prof.DNS.SearchList:
                    dclist.append([domain])

                for host in prof.HostsList:
                    hclist.append([host.IP, host.Hostname, string.join(host.AliasList, ' ')])

        row = 0
        actrow = 0
        for prof in profilelist:
            if prof.Active == true:
               actrow = row
               break
            row = row + 1

        if self.initialized:
            return

        clist = self.xml.get_widget("profileList")
        self.initialized = true
        for prof in profilelist:
            clist.append([prof.ProfileName])
        clist.select_row(actrow, 0)

    def on_Dialog_delete_event(self, *args):
        gtk.mainquit()

    def on_okButton_clicked (self, button):
        self.save()
        gtk.mainquit()

    def on_cancelButton_clicked(self, button):
        gtk.mainquit()

    def on_helpButton_clicked(self, button):
        gnome.help.goto ("/usr/share/doc/redhat-config-network-0.6.7/index.html")

    def on_deviceAddButton_clicked (self, clicked):
        #interface = NewInterface()
        #gtk.mainloop()
        #self.hydrate()
        
        profilelist = getProfileList()
        devicelist = getDeviceList()

        device = Device()

        type = deviceTypeDialog(device, self.xml)
        dialog = type.xml.get_widget ("Dialog")
        button = dialog.run ()
        if button != 0:
            return

        button = self.editDevice(device)
        if button == 0:
            i = devicelist.addDevice()
            devicelist[i].apply(device)
            devicelist[i].commit()
            for prof in profilelist:
                if prof.Active == false:
                    continue
                prof.ActiveDevices.append(device.DeviceId)
                break

            self.hydrate()
        
    def on_deviceCopyButton_clicked (self, button):
        devicelist = getDeviceList()

        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        device = Device()
        device.apply(devicelist[clist.selection[0]])

        duplicate = TRUE
        num = 0
        while duplicate:
            devname = device.DeviceId + 'Copy' + str(num)
            duplicate = FALSE
            for dev in devicelist:
                if dev.DeviceId == devname:
                    duplicate = TRUE
                    break
            num = num + 1
        device.DeviceId = devname

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

        button = self.editDevice(device)

        self.hydrate()

    def editDevice(self, device):
        button = 0
        type = device.Type
        device.createDialup()
        device.createCipe()
        device.createWireless()

        if type == "Ethernet":
            cfg = ethernetConfigDialog(device, self.xml)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == "ISDN":
            cfg = ISDNDialupDialog(device, self.xml)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == "Modem":
            cfg = ModemDialupDialog(device, self.xml)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == "xDSL":
            cfg = dslConfigDialog(device, self.xml)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == "CIPE":
            cfg = cipeConfigDialog(device, self.xml)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == "Wireless":
            cfg = wirelessConfigDialog(device, self.xml)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        else:
            generic_error_dialog ('This device can not be edited with this tool!', self.xml.get_widget ("Dialog"))


        return button

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
                    xpm, mask = get_icon ("pixmaps/active.xpm", self.dialog)
                    clist.set_row_data(row, 1)
                    curr_prof = profilelist[self.xml.get_widget('profileList').selection[0]]
                    if curr_prof.ProfileName == 'default':
                        for prof in profilelist:
                            profilelist.activateDevice(name, prof.ProfileName, true)
                    else:
                        profilelist.activateDevice(name, curr_prof.ProfileName, true)
                else:
                    xpm, mask = get_icon ("pixmaps/inactive.xpm", self.dialog)
                    clist.set_row_data(row, 0)
                    curr_prof = profilelist[self.xml.get_widget('profileList').selection[0]]
                    if curr_prof.ProfileName == 'default':
                        for prof in profilelist:
                            profilelist.activateDevice(name, prof.ProfileName, false)
                    else:
                        profilelist.activateDevice(name, curr_prof.ProfileName, false)
#                        profilelist.activateDevice(name, 'default', false)
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

    def on_tertiaryDnsEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.TertiaryDNS = entry.get_text()

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
        dialog = gnome.ui.GnomeRequestDialog (FALSE, "Please enter the name for the new profile.\nThe name may only contain letters and digits.", "NewProfile", 50, self.on_profileAddEntry_changed, self.dialog)
        dialog.run()

    def on_profileAddEntry_changed(self, text):
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
        prof.DNS.TertiaryDNS   = ''
        prof.DNS.createSearchList()
        self.xml.get_widget("profileList").clear()
        self.initialized = false
        self.hydrate()

    def on_profileCopyButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget("profileList")

        if len(clist.selection) == 0:
            return

        profile = Profile()
        profile.apply(profilelist[clist.selection[0]])

        duplicate = TRUE
        num = 0
        while duplicate:
            profnam = profile.ProfileName + 'Copy' + str(num)
            duplicate = FALSE
            for prof in profilelist:
                if prof.ProfileName == profnam:
                    duplicate = TRUE
                    break
            num = num + 1
        profile.ProfileName = profnam

        i = profilelist.addProfile()
        profilelist[i].apply(profile)
        profilelist[i].commit()
        self.initialized = None
        clist.clear()
        self.hydrate()

    def on_profileRenameButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget("profileList")

        if len(clist.selection) == 0:
            return

        profile = profilelist[clist.selection[0]]

        import gnome
        import gnome.ui
        dialog = gnome.ui.GnomeRequestDialog (FALSE, "Please enter the new name for the profile.\nThe name may only contain letters and digits.", profile.ProfileName, 50, self.on_profileRenameEntry_changed, self.dialog)
        dialog.run()

    def on_profileRenameEntry_changed(self, text):
        if not text or not re.match("^[a-z|A-Z|0-9]+$", text):
            return

        profilelist = getProfileList()

        clist = self.xml.get_widget("profileList")

        if len(clist.selection) == 0:
            return

        profile = profilelist[clist.selection[0]]
        profile.ProfileName = text
        profile.commit()
        self.initialized = None
        clist.clear()
        self.hydrate()

    def on_profileDeleteButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget('profileList')

        if len(clist.selection) == 0:
            return

        if profilelist[clist.selection[0]].ProfileName == 'default':
            generic_error_dialog ('The default Profile can not be deleted!', self.xml.get_widget ("Dialog"))
            return
        del profilelist[clist.selection[0]]
        self.initialized = None
        clist.clear()
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
    progname = os.path.basename(sys.argv[0])
    if progname == 'redhat-config-network' or progname == 'neat' or progname == 'netconf.py':
        window = mainDialog()
    elif progname == 'redhat-config-network-druid' or progname == 'internet-druid':
        interface = NewInterface()

    gtk.mainloop()
    sys.exit(0)
