#! /usr/bin/python2.2

## netconf - A network configuration tool
## Copyright (C) 2001, 2002 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001, 2002 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>
## Copyright (C) 2001, 2002 Trond Eivind Glomsrød <teg@redhat.com>

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
import gettext

PROGNAME='redhat-config-network'
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)

try:
    gettext.install(PROGNAME, "/usr/share/locale", 1)
except IOError:
    import __builtin__
    __builtin__.__dict__['_'] = unicode    

os.environ["PYgtk_FATAL_EXCEPTIONS"] = '1'

import os.path
import string
from netconfpkg import *

def Usage():
    print _("redhat-config-network-cmd - Python network configuration commandline tool\n\nUsage: redhat-config-network-cmd -p --profile <profile>")

# Argh, another workaround for broken gtk/gnome imports...
if __name__ == '__main__':

    if os.getuid() != 0:
        print _("Please restart %s with root permissions!") % (sys.argv[0])
        sys.exit(10)
        
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


from netconfpkg.gui import *
from netconfpkg.Control import *
from netconfpkg.gui.GUI_functions import GLADEPATH
from netconfpkg.gui.exception import handleException
import gtk
import gtk.glade
gtk.glade.bindtextdomain(PROGNAME, "/usr/share/locale")

PROFILE_COLUMN = 0
STATUS_COLUMN = 1
DEVICE_COLUMN = 2
NICKNAME_COLUMN = 3

TRUE=gtk.TRUE
FALSE=gtk.FALSE

showprofile = 0

DEFAULT_PROFILE_NAME=_("Common")

class mainDialog:
    def __init__(self, modus=None):
        glade_file = "maindialog.glade"

        if not os.path.isfile(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=PROGNAME)
        self.initialized = None
        self.no_profileentry_update = None
        self.xml.signal_autoconnect(
            {
            "on_deviceAddButton_clicked" : self.on_deviceAddButton_clicked,
            "on_deviceCopyButton_clicked" : self.on_deviceCopyButton_clicked,
            "on_deviceEditButton_clicked" : self.on_deviceEditButton_clicked,
            "on_deviceDeleteButton_clicked" : self.on_deviceDeleteButton_clicked,
            "on_deviceActivateButton_clicked" : self.on_deviceActivateButton_clicked,
            "on_deviceDeactivateButton_clicked" : self.on_deviceDeactivateButton_clicked,
            "on_deviceMonitorButton_clicked" : self.on_deviceMonitorButton_clicked,
            "on_deviceList_select_row" : (self.on_generic_clist_select_row,
                                          self.xml.get_widget("deviceEditButton"),
                                          self.xml.get_widget("deviceDeleteButton"),
                                          self.xml.get_widget("deviceCopyButton"),
                                          None, None,None,
                                          self.xml.get_widget("deviceActivateButton"),
                                          self.xml.get_widget("deviceDeactivateButton"),
                                          self.xml.get_widget("deviceMonitorButton")),
            "on_deviceList_unselect_row" : (self.on_generic_clist_unselect_row,
                                            self.xml.get_widget("deviceEditButton"),
                                            self.xml.get_widget("deviceDeleteButton"),
                                            self.xml.get_widget("deviceCopyButton")),
            "on_deviceList_button_press_event" : (self.on_generic_clist_button_press_event,
                                                  self.on_deviceEditButton_clicked),
            "on_applyButton_clicked" : self.on_applyButton_clicked,
            "on_okButton_clicked" : self.on_okButton_clicked,
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
            "on_profileDeleteButton_clicked" : self.on_profileDeleteButton_clicked,
            "on_ProfileNameEntry_insert_text" : (self.on_generic_entry_insert_text,
                                                r"^[a-z|A-Z|0-9]+$"),
        })


        self.xml.get_widget ("hardware_pixmap").set_from_file("/usr/share/redhat-config-network/pixmaps/connection-ethernet.png")
        self.xml.get_widget ("hosts_pixmap").set_from_file("/usr/share/redhat-config-network/pixmaps/nameresolution_alias.png")
        self.xml.get_widget ("devices_pixmap").set_from_file("/usr/share/redhat-config-network/pixmaps/network.png")
        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.mainquit)

        
        if showprofile:
            self.xml.get_widget ("profileFrame").show()

        self.on_xpm, self.on_mask = get_icon('pixmaps/on.xpm', self.dialog)
        self.off_xpm, self.off_mask = get_icon('pixmaps/off.xpm', self.dialog)
        self.act_xpm, self.act_mask = get_icon ("pixmaps/active.xpm", self.dialog)
        self.inact_xpm, self.inact_mask = get_icon ("pixmaps/inactive.xpm", self.dialog)
        self.devsel = None

        if not os.access('/usr/bin/rp3', os.X_OK):
            self.xml.get_widget('deviceMonitorButton').hide()
        
        load_icon("network.xpm", self.dialog)
        self.load()
        self.hydrate()
        self.xml.get_widget ("deviceList").column_titles_passive ()
        self.xml.get_widget ("hardwareList").column_titles_passive ()
        self.xml.get_widget ("dnsList").column_titles_passive ()
        self.xml.get_widget ("hostsList").column_titles_passive ()    
        
        if getDeviceList():
            notebook = self.xml.get_widget('mainNotebook')
            widget = self.xml.get_widget('deviceFrame')
            page = notebook.page_num(widget)
            notebook.set_current_page(page)

        self.activedevicelist = NetworkDevice().get()
        self.tag = timeout_add(4000, self.update_devicelist)


        if modus == 'druid': self.on_deviceAddButton_clicked(None)

        # Let this dialog be in the taskbar like a normal window
        self.dialog.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        self.dialog.show()

        
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

    def test(self):
        profilelist = getProfileList()
        devicelist = getDeviceList()
        hardwarelist = getHardwareList()
        
        try:
            hardwarelist.test()
            devicelist.test()
            profilelist.test()
        except TestError, msg:
            generic_error_dialog (str(msg), self.dialog)
            return 1                            
        
        return 0

    def changed(self):
        profilelist = getProfileList()
        devicelist = getDeviceList()
        hardwarelist = getHardwareList()
        
        if profilelist.modified() or \
               devicelist.modified() or hardwarelist.modified():
            return true

        return false

    def save(self):
        if self.test() != 0:
            return 1
        
        self.saveHardware()
        self.saveDevices()
        self.saveProfiles()
        self.checkApply()
        return 0

    def saveDevices(self):
        devicelist = getDeviceList()
        devicelist.save()
        devicelist.setChanged(false)
        
    def saveHardware(self):
        hardwarelist = getHardwareList()
        hardwarelist.save()
        hardwarelist.setChanged(false)
        
    def saveProfiles(self):
        profilelist = getProfileList()
        profilelist.save()
        profilelist.setChanged(false)
        
    def hydrate(self):
        self.hydrateProfiles()
        self.hydrateDevices()
        self.hydrateHardware()
        self.checkApply()

    def checkApply(self, changed = -1):
        if changed == -1:
            changed = self.changed()
        apply_btn = self.xml.get_widget("applyButton")
        if changed:
            apply_btn.set_sensitive (TRUE)
        else:
            apply_btn.set_sensitive (FALSE)
            
            
    def hydrateDevices(self):
        devicelist = getDeviceList()
        activedevicelist = NetworkDevice().get()
        profilelist = getProfileList()
        devsel = self.devsel

        clist = self.xml.get_widget("deviceList")
       
        clist.clear()
        
        clist.set_row_height(17)
        status_pixmap = self.off_xpm
        status_mask = self.off_mask
        status = INACTIVE

        row = 0
        for dev in devicelist:
            devname = dev.getDeviceAlias()

            if devname in activedevicelist:
                status = ACTIVE
                status_pixmap = self.on_xpm
                status_mask = self.on_mask
            else:
                status = INACTIVE
                status_pixmap = self.off_xpm
                status_mask = self.off_mask
                
            device_pixmap, device_mask = \
                GUI_functions.get_device_icon_mask(dev.Type, self.dialog)

            clist.append(['', status, devname, dev.DeviceId, dev.Type])
            clist.set_pixmap(row, PROFILE_COLUMN, self.inact_xpm, self.inact_mask)
            clist.set_pixtext(row, STATUS_COLUMN, status, 5, status_pixmap, status_mask)
            clist.set_pixtext(row, DEVICE_COLUMN, devname, 5, device_pixmap, device_mask)
            clist.set_row_data(row, dev)
            
            for prof in profilelist:
                if (prof.Active == true or prof.ProfileName == 'default') and dev.DeviceId in prof.ActiveDevices:
                    clist.set_pixmap(row, PROFILE_COLUMN, self.act_xpm, self.act_mask)
                    break
                

            if dev == devsel:
                clist.select_row(row, 0)
                
            row = row + 1
        
    def hydrateHardware(self):
        hardwarelist = getHardwareList()

        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        clist.set_row_height(17)
        for hw in hardwarelist:
            clist.append([str(hw.Description), str(hw.Type), str(hw.Name)])

    def hydrateProfiles(self):
        profilelist = getProfileList()

        dclist = self.xml.get_widget("dnsList")
        dclist.clear()
        dclist.set_row_height(17)
        hclist = self.xml.get_widget("hostsList")
        hclist.clear()
        hclist.set_row_height(17)
        for prof in profilelist:
            if prof.Active != true:
                continue
            if prof.DNS.Hostname:
                self.xml.get_widget('hostnameEntry').set_text(\
                    prof.DNS.Hostname)
            else: self.xml.get_widget('hostnameEntry').set_text('')
            if prof.DNS.Domainname:
                self.xml.get_widget('domainnameEntry').set_text(\
                    prof.DNS.Domainname)
            else: self.xml.get_widget('domainnameEntry').set_text('')
            if prof.DNS.PrimaryDNS:
                self.xml.get_widget('primaryDnsEntry').set_text(\
                    prof.DNS.PrimaryDNS)
            else: self.xml.get_widget('primaryDnsEntry').set_text('')
            if prof.DNS.SecondaryDNS:
                self.xml.get_widget('secondaryDnsEntry').set_text(\
                    prof.DNS.SecondaryDNS)
            else: self.xml.get_widget('secondaryDnsEntry').set_text('')
            if prof.DNS.TertiaryDNS:
                self.xml.get_widget('tertiaryDnsEntry').set_text(\
                    prof.DNS.TertiaryDNS)
            else: self.xml.get_widget('tertiaryDnsEntry').set_text('')
            for domain in prof.DNS.SearchList:
                dclist.append([domain])

            for host in prof.HostsList:
                hclist.append([host.IP, host.Hostname,
                               string.join(host.AliasList, ' ')])
            break

            
        if self.initialized:
            return

        self.initialized = true

        self.xml.get_widget ("searchDnsEntry").set_text ("")
        self.no_profileentry_update = true
        omenu = self.xml.get_widget('profileOption')
        omenu.remove_menu ()
        menu = gtk.Menu ()
        history = 0
        i = 0
        for prof in profilelist:
            name = prof.ProfileName
            # change the default profile to a more understandable name
            if name == "default":
                name = _(DEFAULT_PROFILE_NAME)
            menu_item = gtk.MenuItem (name)
            menu_item.show ()
            menu_item.connect ("activate",
                               self.on_profileMenuItem_activated,
                               prof.ProfileName)
            menu.append (menu_item)
            if prof.ProfileName == self.get_active_profile().ProfileName:
                history = i
            i = i+1
        menu.show ()
        omenu.set_menu (menu)
        omenu.set_history (history)
        menu.get_children()[history].activate ()
        self.no_profileentry_update = false

    def on_Dialog_delete_event(self, *args):
        if self.changed():        
            button = generic_yesno_dialog(
                _("Do you want to save your changes?"),
                self.dialog)
            if button == gtk.RESPONSE_YES:
                self.save()
            
        gtk.mainquit()

    def on_applyButton_clicked (self, button):
        self.save()

    def on_okButton_clicked (self, *args):        
        if self.changed():        
            button = generic_yesnocancel_dialog(
                _("Do you want to save your changes?"),
                self.dialog)
            
            if button == gtk.RESPONSE_YES:
                if self.save() != 0:
                    return
            
            if button == gtk.RESPONSE_CANCEL:
                return
            
        gtk.mainquit()

    def on_helpButton_clicked(self, button):
        import gnome
        gnome.url_show("file:///usr/share/redhat-config-network/help/index.html")

    def on_deviceAddButton_clicked (self, clicked):
        #profilelist = getProfileList()
        #devicelist = getDeviceList()
        
        interface = NewInterfaceDialog()
        
        interface.toplevel.set_transient_for(self.dialog)

        gtk.mainloop()            
            
        self.hydrate()
        
    def on_deviceCopyButton_clicked (self, button):
        devicelist = getDeviceList()

        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        device = Device()
        device.apply(clist.get_row_data(clist.selection[0]))

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

        device = clist.get_row_data(clist.selection[0])

        if device.Type == LO:
            generic_error_dialog (_('The Loopback device can not be edited!'), self.dialog)
            return

        devId = device.DeviceId
        button = self.editDevice(device)

        if button != gtk.RESPONSE_OK and button != 0:
            device.rollback()
            return

        device.commit()

        if not device.modified():
            return

        # Fixed change device names in active list of all profiles
        profilelist = getProfileList()
        for prof in profilelist:
            if devId in prof.ActiveDevices:
                pos = prof.ActiveDevices.index(devId)
                prof.ActiveDevices[pos] = device.DeviceId
                prof.commit()

        self.hydrate()
        device.changed = false

    def editDevice(self, device):
        button = 0
        type = device.Type
        device.createDialup()
        device.createCipe()
        device.createWireless()

        if type == ETHERNET:
            cfg = ethernetConfigDialog(device)

        elif type == TOKENRING:
            cfg = tokenringConfigDialog(device)

        elif type == ISDN:
            cfg = ISDNDialupDialog(device)

        elif type == MODEM:
            cfg = ModemDialupDialog(device)

        elif type == DSL:
            cfg = dslConfigDialog(device)

        elif type == CIPE:
            cfg = cipeConfigDialog(device)

        elif type == WIRELESS:
            cfg = wirelessConfigDialog(device)

        elif type == CTC or type == IUCV:
            cfg = ctcConfigDialog(device)

        else:
            generic_error_dialog (_('This device can not be edited with this tool!'), self.dialog)
            return button
            
        dialog = cfg.xml.get_widget ("Dialog")
        dialog.set_transient_for(self.dialog)
        button = dialog.run()
        dialog.destroy()

        return button

    def on_deviceDeleteButton_clicked (self, button):
        devicelist = getDeviceList()
        profilelist = getProfileList()

        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        device = clist.get_row_data(clist.selection[0])

        if device.Type == 'Loopback':
            generic_error_dialog (_('The Loopback device can not be removed!'), self.dialog)
            return

        buttons = generic_yesno_dialog((_('Do you really want to delete device "%s"?')) % str(device.DeviceId), self.dialog, widget = clist, page = clist.selection[0])

        if buttons != gtk.RESPONSE_YES:
            return

        for prof in profilelist:
            if device.DeviceId in prof.ActiveDevices:
                pos = prof.ActiveDevices.index(device.DeviceId)
                del prof.ActiveDevices[pos]
        profilelist.commit()
        
        del devicelist[devicelist.index(device)]
        devicelist.commit()
        self.hydrate()

    def on_deviceActivateButton_clicked(self, button):
        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return
        
        dev = clist.get_row_data(clist.selection[0])
        device = dev.getDeviceAlias()

        timeout_remove(self.tag)
        
        if dev.changed:
            button = generic_yesno_dialog(
                _("You have made some changes in your configuration.") + "\n" +\
                _("To activate the network device %s, the changes have to be saved.") % (device) +\
                "\n\n" +\
                _("Do you want to continue?") ,
                self.dialog)
                
            if button == gtk.RESPONSE_YES:
                if self.save() != 0:
                    return
            
            if button == gtk.RESPONSE_NO:
                return

        intf = Interface()
        child = intf.activate(device)
        dlg = gtk.Dialog(_('Network device activating...'))
        dlg.set_border_width(10)
        dlg.vbox.add(gtk.Label(_('Activating network device %s, please wait...') %(device)))
        dlg.vbox.show()
        dlg.set_position (gtk.WIN_POS_MOUSE)
        dlg.set_modal(TRUE)
        dlg.show_all()
        idle_func()
        os.waitpid(child, 0)
        dlg.destroy()

        if NetworkDevice().find(device):
            self.update_devicelist()
        else:
            devErrorDialog(device, ACTIVATE, self.dialog)

        self.tag = timeout_add(4000, self.update_devicelist)
            
    def on_deviceDeactivateButton_clicked(self, button):
        clist = self.xml.get_widget("deviceList")
        if len(clist.selection) == 0:
            return
        
        device = clist.get_row_data(clist.selection[0]).getDeviceAlias()
        
        if device:
            intf = Interface()
            ret = intf.deactivate(device)
            if not ret:
                self.update_devicelist()
            else:
                devErrorDialog(device, DEACTIVATE, self.dialog)

    def on_deviceMonitorButton_clicked(self, button):
        generic_error_dialog(_("To be rewritten!"))
        return
        device = clist.get_row_data(clist.selection[0]).getDeviceAlias()
        if device:
            Interface().monitor(device)
    
    def clist_get_status(self):
        clist = self.xml.get_widget('deviceList')
        if len(clist.selection) == 0:
            return
        if not clist.get_row_data(clist.selection[0]):
            return
        dev = clist.get_pixtext(clist.selection[0], STATUS_COLUMN)[0]
        return dev

    def clist_get_device(self):
        clist = self.xml.get_widget('deviceList')
        if len(clist.selection) == 0:
            return
        if not clist.get_row_data(clist.selection[0]):
            return
        dev = clist.get_pixtext(clist.selection[0], DEVICE_COLUMN)[0]
        return dev

    def clist_get_nickname(self):
        clist = self.xml.get_widget('deviceList')
        if len(clist.selection) == 0:
            return
        if not clist.get_row_data(clist.selection[0]):
            return
        dev = clist.get_text(clist.selection[0], NICKNAME_COLUMN)
        return dev

    def update_devicelist(self):
        activedevicelistold = self.activedevicelist
        self.activedevicelist = NetworkDevice().get()

        if activedevicelistold != self.activedevicelist:
            self.hydrateDevices()
            return TRUE

        return TRUE
    
    def on_generic_entry_insert_text(self, entry, partial_text, length, pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_profileMenuItem_activated(self, menu_item, profile):
        if profile == 'default':
            self.xml.get_widget ('profileRenameButton').set_sensitive (FALSE)
            self.xml.get_widget ('profileDeleteButton').set_sensitive (FALSE)
        else:
            self.xml.get_widget ('profileRenameButton').set_sensitive (TRUE)
            self.xml.get_widget ('profileDeleteButton').set_sensitive (TRUE)
        if not self.no_profileentry_update:
            profilelist = getProfileList ()
            for prof in profilelist:
                if prof.ProfileName == profile:
                    prof.Active = true
                    #print "profile " + prof.ProfileName + " activated\n"
                else: prof.Active = false
                prof.commit()
            self.hydrate()
        

    def on_generic_clist_select_row(self, clist, row, column, event,
                                    edit_button = None, delete_button = None,
                                    copy_button = None, rename_button = None,
                                    up_button = None, down_button = None,
                                    activate_button = None,
                                    deactivate_button = None,
                                    monitor_button = None):
        devicelist = getDeviceList()

        if edit_button: edit_button.set_sensitive(TRUE)
        if rename_button: rename_button.set_sensitive(TRUE)
        if delete_button: delete_button.set_sensitive(TRUE)
        if copy_button: copy_button.set_sensitive(TRUE)
        if up_button: delete_button.set_sensitive(TRUE)
        if down_button: copy_button.set_sensitive(TRUE)

        if clist.get_name() == 'deviceList':
            if len(clist.selection) == 0:
                return
            
            self.devsel = clist.get_row_data(clist.selection[0])
            
            status = self.clist_get_status()

            if status == ACTIVE:
                activate_button.set_sensitive(FALSE)
                deactivate_button.set_sensitive(TRUE)
                #edit_button.set_sensitive(FALSE)
                delete_button.set_sensitive(FALSE)
                monitor_button.set_sensitive(TRUE)
            else:
                activate_button.set_sensitive(TRUE)
                deactivate_button.set_sensitive(FALSE)
                #edit_button.set_sensitive(TRUE)
                delete_button.set_sensitive(TRUE)
                monitor_button.set_sensitive(FALSE)


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
        #clist.remove_data ("signal_id")
        apply (func)

    def get_active_profile(self):
        profilelist = getProfileList()
        for prof in profilelist:
            if not prof.Active:
                continue
            return prof

        return profilelist[0]

    def on_generic_clist_button_press_event(self, clist, event, func):
        profilelist = getProfileList()

        # don't allow user to edit device if it's active
        #if clist.get_name() == 'deviceList':
        #    try:
        #        status = clist.get_pixtext(clist.selection[0], 0)[0]
        #    except ValueError:
        #        status = clist.get_text(clist.selection[0], 0)

        #    if status == ACTIVE:
        #        return
                
        if event.type == gtk.gdk._2BUTTON_PRESS:
            info = clist.get_selection_info(event.x, event.y)
            if info != None and info[1] > 0:
                id = clist.connect("button_release_event",
                                   self.on_generic_clist_button_release_event,
                                   func)
                clist.set_data("signal_id", id)
                 
        if clist.get_name() == 'deviceList' and gtk.gdk.BUTTON_PRESS:
             info = clist.get_selection_info(event.x, event.y)
             if info != None and info[1] == 0:
                 row = info[0]

                 device = clist.get_row_data(row)
                 name = device.DeviceId
                 type = device.Type
                 if type == LO:
                     generic_error_dialog (_('The Loopback device can not be disabled!'), self.dialog)
                     return

                 curr_prof = self.get_active_profile()

                 if device.DeviceId not in curr_prof.ActiveDevices:
                     xpm, mask = self.act_xpm, self.act_mask
                     curr_prof = self.get_active_profile()
                     if curr_prof.ProfileName == 'default':
                         for prof in profilelist:
                             profilelist.activateDevice(name, prof.ProfileName, true)
                     else:
                         profilelist.activateDevice(name, curr_prof.ProfileName, true)
                         for prof in profilelist:
                             if prof.ProfileName == "default":
                                 continue
                             if name not in prof.ActiveDevices:
                                 break
                         else:
                             profilelist.activateDevice(name, 'default', true)
                        
                 else:
                     xpm, mask = self.inact_xpm, self.inact_mask
                     if curr_prof.ProfileName == 'default':
                         for prof in profilelist:
                             profilelist.activateDevice(name, prof.ProfileName, false)
                     else:
                         profilelist.activateDevice(name, curr_prof.ProfileName, false)
                         profilelist.activateDevice(name, 'default', false)

                 for prof in profilelist:
                     prof.commit()
                 
                 clist.set_pixmap(row, PROFILE_COLUMN, xpm, mask)
                 self.checkApply()
                 
    def on_hostnameEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.Hostname = entry.get_text()
                prof.DNS.commit()
                break
        self.checkApply()
        
    def on_domainEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.Domainname = entry.get_text()
                prof.DNS.commit()
                break
        self.checkApply()
            
    def on_primaryDnsEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.PrimaryDNS = entry.get_text()
                prof.DNS.commit()
                break
        self.checkApply()
            
    def on_secondaryDnsEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.SecondaryDNS = entry.get_text()
                prof.DNS.commit()
                break
        self.checkApply()
            
    def on_tertiaryDnsEntry_changed(self, entry):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                prof.DNS.TertiaryDNS = entry.get_text()
                prof.DNS.commit()
                break
        self.checkApply()
            
    def on_searchDnsEntry_changed(self, entry):
        if len (string.strip (entry.get_text ())) == 0:
            self.xml.get_widget ("dnsAddButton").set_sensitive (FALSE)
        else:
            self.xml.get_widget ("dnsAddButton").set_sensitive (TRUE)

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
                break
            
        self.hydrate()
        self.xml.get_widget("searchDnsEntry").grab_focus ()

    def on_dnsEditButton_clicked (self, *args):
        clist = self.xml.get_widget("dnsList")

        if len(clist.selection) == 0:
            return

        name = clist.get_text(clist.selection[0], 0)

        dialog = editDomainDialog(name)
        dialog.main = self
        dlg = dialog.xml.get_widget("Dialog")
        dlg.set_transient_for(self.dialog)
        button = dlg.run()
        dialog.xml.get_widget("Dialog").destroy()

        if button != gtk.RESPONSE_OK and button != 0:            
            return
                
        self.hydrate()

    def on_dnsUpButton_clicked (self, button):
        profilelist = getProfileList()

        clist = self.xml.get_widget("dnsList")
        if len(clist.selection) == 0 or clist.selection == 0:
            return
        name = clist.get_text(clist.selection[0], 0)

        for prof in profilelist:
            if prof.Active == true:
                index = prof.DNS.SearchList.index(name)
                if index == 0:
                    return

                n = prof.DNS.SearchList[index-1]
                prof.DNS.SearchList[index-1] = name
                prof.DNS.SearchList[index] = n
                prof.DNS.SearchList.commit()
                clist.select_row(index-1, 0)
                break

        self.hydrate()

    def on_dnsDownButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget("dnsList")
        if len(clist.selection) == 0 or clist.selection == 0:
            return
        name = clist.get_text(clist.selection[0], 0)

        for prof in profilelist:
            if prof.Active == true:
                index = prof.DNS.SearchList.index(name)
                if len(prof.DNS.SearchList) == index + 1:
                    return

                n = prof.DNS.SearchList[index+1]
                prof.DNS.SearchList[index+1] = name
                prof.DNS.SearchList[index] = n
                prof.DNS.SearchList.commit()
                clist.select_row(index+1, 0)
                break
            
        self.hydrate()

    def on_dnsDeleteButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget("dnsList")
        if len(clist.selection) == 0:
            return

        for prof in profilelist:
            if prof.Active == true:
                del prof.DNS.SearchList[clist.selection[0]]
                prof.DNS.SearchList.commit()
                break
            
        self.hydrate()

    def on_hostsAddButton_clicked(self, *args):
        profilelist = getProfileList()

        curr_prof = self.get_active_profile()
        if not curr_prof.HostsList:
            curr_prof.createHostsList()
        hostslist = curr_prof.HostsList
        host = Host()
        clist  = self.xml.get_widget("hostsList")
        dialog = editHostsDialog(host)
        dl = dialog.xml.get_widget ("Dialog")
        dl.set_transient_for(self.dialog)
        button = dl.run ()
        dl.destroy()
        if button != gtk.RESPONSE_OK and button != 0:
            return
        
        i = hostslist.addHost()
        hostslist[i].apply(host)
        hostslist[i].commit()
        self.hydrate()

    def on_hostsEditButton_clicked (self, *args):
        profilelist = getProfileList()

        curr_prof = self.get_active_profile()
        hostslist = curr_prof.HostsList
        clist  = self.xml.get_widget("hostsList")

        if len(clist.selection) == 0:
            return

        host = hostslist[clist.selection[0]]

        dialog = editHostsDialog(host)
        dl = dialog.xml.get_widget ("Dialog")
        dl.set_transient_for(self.dialog)
        button = dl.run ()
        dl.destroy()
        if button != gtk.RESPONSE_OK and button != 0:
            host.rollback()
            return
        host.commit()
        if host.changed:
            self.hydrate()
            host.changed = false

    def on_hostsDeleteButton_clicked (self, *args):
        profilelist = getProfileList()

        clist = self.xml.get_widget('profileList')

        #if len(clist.selection) == 0:
        #    return
        #
        prof = self.get_active_profile()

        clist = self.xml.get_widget('hostsList')

        if len(clist.selection) == 0:
            return

        todel = list(clist.selection)
        todel.sort()
        todel.reverse()

        for i in todel:
            del prof.HostsList[i]
            
        prof.HostsList.commit()
        self.hydrate()

    def on_profileList_click_column (self, *args):
        pass

    def on_profileList_select_row (self, *args):
        pass

    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_profileAddButton_clicked (self, *args):
        dialog = self.xml.get_widget("ProfileNameDialog")
        dialog.set_transient_for(self.dialog)
        self.xml.get_widget("ProfileName").set_text('')
        dialog.show()
        button = dialog.run()        
        dialog.hide()

        if button != gtk.RESPONSE_OK and button != 0:
            return

        profilelist = getProfileList()

        text = self.xml.get_widget("ProfileName").get_text()

        if not text:
            return
        
        if not re.match("^[a-z|A-Z|0-9]+$", text):
            generic_error_dialog (_('The name may only contain letters and digits!'), self.dialog)
            return 1

        if text == 'default' or text == DEFAULT_PROFILE_NAME:
            generic_error_dialog (_('The profile can\'t be named "%s"!') % text, self.dialog)
            return 1

        for prof in profilelist:
            if prof.ProfileName == text:
                generic_error_dialog (_('The profile name already exists!'), self.dialog)
                return 1

        i = profilelist.addProfile()
        prof = profilelist[i]
        prof.apply(profilelist[0])
        prof.ProfileName = text
        for p in profilelist:
            p.Active = false
            
        prof.Active = true

        prof.commit()
        
        #self.xml.get_widget("profileList").clear()
        self.initialized = false
        self.hydrate()
        return 0

    def on_profileCopyButton_clicked (self, *args):
        profilelist = getProfileList()

        profile = Profile()
        profile.apply(self.get_active_profile())

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
        #clist.clear()        
        self.hydrate()

    def on_profileRenameButton_clicked (self, *args):
        profilelist = getProfileList()
        
        profile = self.get_active_profile()
        if profile.ProfileName == 'default':
            generic_error_dialog (_('The "default" profile can\'t be renamed!'), self.dialog)
            return

        dialog = self.xml.get_widget("ProfileNameDialog")
        dialog.set_transient_for(self.dialog)
        self.xml.get_widget("ProfileName").set_text(profile.ProfileName)
        dialog.show()
        button = dialog.run()        
        dialog.hide()

        if button != gtk.RESPONSE_OK and button != 0:
            return

        text = self.xml.get_widget("ProfileName").get_text()

        if not text:
            return
        
        if not re.match("^[a-z|A-Z|0-9]+$", text):
            generic_error_dialog (_('The name may only contain letters and digits!'), self.dialog)
            return

        if text == 'default' or text == DEFAULT_PROFILE_NAME:
            generic_error_dialog (_('The profile can\'t be named "%s"!') % text, self.dialog)
            return

        for prof in profilelist:
            if prof.ProfileName == text and prof != profile:
                generic_error_dialog (_('The profile name already exists!'), self.dialog)
                return

        profile.ProfileName = text
        profile.commit()        
        self.initialized = None
        if profile.changed:
            self.hydrate()
            profile.changed = false

    def on_profileDeleteButton_clicked (self, *args):
        profilelist = getProfileList()

        #clist = self.xml.get_widget('profileList')

        #if len(clist.selection) == 0:
        #    return

        name = self.get_active_profile().ProfileName

        if name == 'default':
            generic_error_dialog(_('The "default" Profile can not be deleted!'), self.dialog)
            return

        buttons = generic_yesno_dialog((_('Do you really want to delete profile "%s"?')) % str(name), self.dialog)

        if buttons != gtk.RESPONSE_YES:
            return

        del profilelist[profilelist.index(self.get_active_profile())]
        profilelist.commit()
        profilelist[0].Active = true
        self.initialized = None
        #clist.clear()
        self.hydrate()

    def on_hardwareAddButton_clicked (self, *args):
        device = Device()

        type = hardwareTypeDialog()
        dialog = type.xml.get_widget ("Dialog")

        button = dialog.run ()
        dialog.set_transient_for(self.dialog)
        dialog.destroy()

        if button != gtk.RESPONSE_OK and button != 0:
            return

        type = type.type
        self.showHardwareDialog(type, false)

    def on_hardwareEditButton_clicked (self, *args):
        clist = self.xml.get_widget('hardwareList')

        if len(clist.selection) == 0:
            return

        type  = clist.get_text(clist.selection[0], 1)
        self.showHardwareDialog(type, true)

    def showHardwareDialog(self, deviceType, edit):
        hardwarelist = getHardwareList()

        if deviceType == ETHERNET or deviceType == TOKENRING  or  \
           deviceType == 'Pocket (ATP)' or deviceType == 'Arcnet':
            if not edit:
                hw = Hardware()
                hw.Type = deviceType
                hw.createCard()
            else:
                clist = self.xml.get_widget('hardwareList')

                if len(clist.selection) == 0:
                    return

                hw = hardwarelist[clist.selection[0]]
	    if deviceType == TOKENRING:
            	dialog = tokenringHardwareDialog(hw)
	    else:
            	dialog = ethernetHardwareDialog(hw)

        if deviceType == MODEM:
            if edit:
                clist = self.xml.get_widget('hardwareList')
                type  = clist.get_text(clist.selection[0], 1)
                dev   = clist.get_text(clist.selection[0], 2)
                for hw in hardwarelist:
                    if hw.Name == dev:
                        break;
            else:
                hw = Hardware()
                hw.Description = 'Generic Modem'
                hw.Type = MODEM
                hw.createModem()
            
            dialog = modemDialog(hw)

        if deviceType == ISDN:
            if edit:
                clist = self.xml.get_widget('hardwareList')
                Description = clist.get_text(clist.selection[0], 0)
                type  = clist.get_text(clist.selection[0], 1)
                dev   = clist.get_text(clist.selection[0], 2)
                for hw in hardwarelist:
                    if hw.Description == Description:
                        break;
            else:
                hw = Hardware()
                hw.Type = ISDN
                hw.createCard()

            dialog = isdnHardwareDialog(hw)
            
        dl = dialog.xml.get_widget('Dialog')
        dl.set_transient_for(self.dialog)
        button = dl.run()
        dl.destroy()
        
        if button != gtk.RESPONSE_OK and button != 0:
            if edit:
                hw.rollback()
            #hardwarelist.rollback()
            return
        
        if not edit:
            i = hardwarelist.addHardware()
            hardwarelist[i].apply(hw)
            hardwarelist[i].commit()
            hardwarelist.commit()
        else:
            hw.commit()

        if hardwarelist.changed:
            self.hydrate()
            hw.changed = false

    def on_hardwareDeleteButton_clicked (self, *args):
        hardwarelist = getHardwareList()

        clist = self.xml.get_widget("hardwareList")

        if len(clist.selection) == 0:
            return

        hw = hardwarelist[clist.selection[0]]
        description = clist.get_text(clist.selection[0], 0)
        type = clist.get_text(clist.selection[0], 1)
        dev = clist.get_text(clist.selection[0], 2)

        buttons = generic_yesno_dialog((_('Do you really want to delete "%s"?')) % str(description),
                                       self.dialog, widget = clist, page = clist.selection[0])

        if buttons != gtk.RESPONSE_YES:
            return

        # remove hardware
        del hardwarelist[clist.selection[0]]
        hardwarelist.commit()

        # remove all devices used this hardware
        devicelist = getDeviceList()
        profilelist = getProfileList()
        dlist = []
        for d in devicelist:
            found = FALSE
            if type == MODEM:
                if d.Dialup and d.Dialup.Inherits and dev == d.Dialup.Inherits:
                    found = TRUE
            elif type == ISDN and d.Type == ISDN:
                found = TRUE
            elif type == ETHERNET:
                if d.Dialup and d.Dialup.EthDevice == dev:
                    found = TRUE
                elif d.Cipe and d.Cipe.TunnelDevice == dev:
                    found = TRUE
                elif d.Wireless and d.Device == dev:
                    found = TRUE
                elif d.Device == dev:
                    found = TRUE
            elif type == TOKENRING and d.Device == dev:
                found = TRUE
            if found: dlist.append(d)
            
        for i in dlist:
            for prof in profilelist:
                if i.DeviceId in prof.ActiveDevices:
                    pos = prof.ActiveDevices.index(i.DeviceId)
                    del prof.ActiveDevices[pos]
            devicelist.remove(i)
            
        devicelist.commit()
        self.hydrate()

# make ctrl-C work
if __name__ == '__main__':
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    progname = os.path.basename(sys.argv[0])

    showprofile = 1

    try:
        opts, args = getopt.getopt(cmdline, "pn", ["profile", "noprofile"])
        for opt, val in opts:
            if opt == '-p' or opt == '--profile':
                showprofile = 1
            if opt == '-n' or opt == '--noprofile':
                showprofile = 0
            else: raise BadUsage

    except (getopt.error, BadUsage):
        Usage()
        sys.exit(1)

    sys.excepthook = lambda type, value, tb: handleException((type, value, tb))
    
    try:
        if progname == 'redhat-config-network' or progname == 'neat' or progname == 'netconf.py':
            window = mainDialog()
        elif progname == 'redhat-config-network-druid' or progname == 'internet-druid':
            window = mainDialog('druid')
            
        gtk.main()

    except SystemExit, code:
        print "Exception %s: %s" % (str(SystemExit), str(code))
        sys.exit(0)
    except:
        handleException(sys.exc_info())

    sys.exit(0)
