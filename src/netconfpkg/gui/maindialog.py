#!/usr/bin/python2.2

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
from netconfpkg import *
from netconfpkg.gui import *
from netconfpkg.Control import *
from netconfpkg.gui.GUI_functions import GLADEPATH
from netconfpkg.gui.GUI_functions import PROGNAME
import gtk
import gtk.glade
import gnome.ui


PROFILE_COLUMN = 0
STATUS_COLUMN = 1
DEVICE_COLUMN = 2
NICKNAME_COLUMN = 3

TRUE=gtk.TRUE
FALSE=gtk.FALSE

PAGE_DEVICES = 0
PAGE_HARDWARE = 1
PAGE_DNS = 2
PAGE_HOSTS = 3

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
            "on_deviceActivateButton_clicked" : \
            self.on_deviceActivateButton_clicked,
            "on_deviceDeactivateButton_clicked" : \
            self.on_deviceDeactivateButton_clicked,
            "on_deviceMonitorButton_clicked" : \
            self.on_deviceMonitorButton_clicked,
            "on_deviceList_select_row" : ( \
            self.on_generic_clist_select_row,
            self.xml.get_widget("editButton"),
            self.xml.get_widget("deleteButton"),
            self.xml.get_widget("copyButton"),
            None, None,None,
            self.xml.get_widget("deviceActivateButton"),
            self.xml.get_widget("deviceDeactivateButton"),
            self.xml.get_widget("deviceMonitorButton")),
            "on_deviceList_unselect_row" : ( \
            self.on_generic_clist_unselect_row,
            self.xml.get_widget("editButton"),
            self.xml.get_widget("deleteButton"),
            self.xml.get_widget("copyButton")),
            "on_deviceList_button_press_event" : ( \
            self.on_generic_clist_button_press_event,
            self.on_deviceEditButton_clicked),
            "on_save_activate" : self.on_applyButton_clicked,
            "on_quit_activate" : self.on_okButton_clicked,
            "on_contents_activate" : self.on_helpButton_clicked,
            "on_hardwareList_select_row" : ( \
            self.on_generic_clist_select_row,
            self.xml.get_widget("editButton"),
            self.xml.get_widget("deleteButton")),
            "on_hardwareList_unselect_row" : ( \
            self.on_generic_clist_unselect_row,
            self.xml.get_widget("editButton"),
            self.xml.get_widget("deleteButton")),
            "on_hardwareList_button_press_event" : ( \
            self.on_generic_clist_button_press_event,
            self.on_hardwareEditButton_clicked),
            "on_hostnameEntry_changed" : self.on_hostnameEntry_changed,
            "on_domainEntry_changed" : self.on_domainEntry_changed,
            "on_primaryDnsEntry_changed" : self.on_primaryDnsEntry_changed,
            "on_secondaryDnsEntry_changed" : self.on_secondaryDnsEntry_changed,
            "on_tertiaryDnsEntry_changed" : self.on_tertiaryDnsEntry_changed,
            "on_searchDnsEntry_changed" : self.on_searchDnsEntry_changed,
            "on_profileAddMenu_activate" : self.on_profileAddMenu_activate,
            "on_profileCopyMenu_activate" : self.on_profileCopyMenu_activate,
            "on_profileRenameMenu_activate": \
            self.on_profileRenameMenu_activate,
            "on_profileDeleteMenu_activate" : \
            self.on_profileDeleteMenu_activate,
            "on_ProfileNameEntry_insert_text" : ( \
            self.on_generic_entry_insert_text, r"^[a-z|A-Z|0-9]+$"),
            "on_about_activate" : self.on_about_activate,
            "on_mainNotebook_switch_page" : self.on_mainNotebook_switch_page,
            "on_addButton_clicked" : self.on_addButton_clicked,
            "on_editButton_clicked" : self.on_editButton_clicked,
            "on_deleteButton_clicked" : self.on_deleteButton_clicked,
            "on_copyButton_clicked" : self.on_copyButton_clicked,
            "on_upButton_clicked" : self.on_upButton_clicked,
            "on_downButton_clicked" : self.on_downButton_clicked,
        })

        self.appBar = self.xml.get_widget ("appbar")

        self.xml.get_widget ("hardware_pixmap").set_from_file( \
            NETCONFDIR + "/pixmaps/connection-ethernet.png")
        self.xml.get_widget ("hosts_pixmap").set_from_file( \
            NETCONFDIR + "/pixmaps/nameresolution_alias.png")
        self.xml.get_widget ("dns_pixmap").set_from_file( \
            NETCONFDIR + "/pixmaps/nameresolution_alias.png")
        self.xml.get_widget ("devices_pixmap").set_from_file( \
            NETCONFDIR + "/pixmaps/network.png")
        
        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.mainquit)

        
        self.xml.get_widget ("profileMenu").show()
            
        self.on_xpm, self.on_mask = get_icon('pixmaps/on.xpm', self.dialog)
        self.off_xpm, self.off_mask = get_icon('pixmaps/off.xpm', self.dialog)
        self.act_xpm, self.act_mask = get_icon ("pixmaps/active.xpm",
                                                self.dialog)
        self.inact_xpm, self.inact_mask = get_icon ("pixmaps/inactive.xpm",
                                                    self.dialog)
        self.devsel = None

        if not os.access('/usr/bin/rp3', os.X_OK):
            self.xml.get_widget('deviceMonitorButton').hide()
        
        load_icon("network.xpm", self.dialog)

        self.load()
        self.hydrate()
        self.xml.get_widget ("deviceList").column_titles_passive ()
        self.xml.get_widget ("hardwareList").column_titles_passive ()
        self.xml.get_widget ("hostsList").column_titles_passive ()    
        
        notebook = self.xml.get_widget('mainNotebook')
        widget = self.xml.get_widget('deviceFrame')
        page = notebook.page_num(widget)
        notebook.set_current_page(page)

        self.page_num = {
            PAGE_DEVICES : notebook.page_num(\
            self.xml.get_widget('deviceFrame')),
            PAGE_HARDWARE : notebook.page_num(\
            self.xml.get_widget('hardwareFrame')),
            PAGE_HOSTS : notebook.page_num(\
            self.xml.get_widget('hostFrame')),
            PAGE_DNS : notebook.page_num(\
            self.xml.get_widget('dnsFrame')),
            }

        self.addButtonFunc = {
            PAGE_DEVICES : self.on_deviceAddButton_clicked,
            PAGE_HARDWARE : self.on_hardwareAddButton_clicked,
            PAGE_HOSTS : self.on_hostsAddButton_clicked,
            }
        self.editButtonFunc = {
            PAGE_DEVICES : self.on_deviceEditButton_clicked,
            PAGE_HARDWARE : self.on_hardwareEditButton_clicked,
            PAGE_HOSTS : self.on_hostsEditButton_clicked,
            }
        self.copyButtonFunc = {
            PAGE_DEVICES : self.on_deviceCopyButton_clicked,
            PAGE_HARDWARE : self.nop,
            PAGE_HOSTS : self.nop,
            }
        self.deleteButtonFunc = {
            PAGE_DEVICES : self.on_deviceDeleteButton_clicked,
            PAGE_HARDWARE : self.on_hardwareDeleteButton_clicked,
            PAGE_HOSTS : self.on_hostsDeleteButton_clicked,
            }
        
        self.activedevicelist = NetworkDevice().get()
        self.tag = timeout_add(4000, self.update_devicelist)

        if modus == 'druid':
            if not self.on_deviceAddButton_clicked(None):
                sys.exit(1)                
                
        # initialize the button state..
        clist = self.xml.get_widget("deviceList")
        self.on_generic_clist_select_row(\
            clist, 0, 0, 0,
            edit_button = self.xml.get_widget("editButton"),
            delete_button = self.xml.get_widget("deleteButton"),
            copy_button = self.xml.get_widget("copyButton"),
            activate_button = self.xml.get_widget("deviceActivateButton"),
            deactivate_button = self.xml.get_widget("deviceDeactivateButton"),
            monitor_button = self.xml.get_widget("deviceMonitorButton"))
        
        # Let this dialog be in the taskbar like a normal window
        #self.dialog.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)

        gtk.Tooltips().enable()
        
        self.dialog.show()
        self.on_mainNotebook_switch_page(None, None,
                                         self.page_num[PAGE_DEVICES])


    def nop(self, *args):
        pass

    def load(self):
        self.appBar.push(_("Loading Configuration..."))
        self.loadDevices()
        self.loadHardware()
        self.loadProfiles()
        self.appBar.pop()

    def loadDevices(self):
        self.appBar.push(_("Loading Device Configuration..."))
        devicelist = getDeviceList()
        self.appBar.pop()
        
    def loadHardware(self):
        self.appBar.push(_("Loading Hardware Configuration..."))
        hardwarelist = getHardwareList()
        self.appBar.pop()

    def loadProfiles(self):
        self.appBar.push(_("Loading Profile Configuration..."))
        profilelist = getProfileList()
        self.appBar.pop()

    def test(self):
        self.appBar.push(_("Testing Configuration Set..."))
        profilelist = getProfileList()
        devicelist = getDeviceList()
        hardwarelist = getHardwareList()
        
        try:
            hardwarelist.test()
            devicelist.test()
            profilelist.test()
        except TestError, msg:
            generic_error_dialog (str(msg), self.dialog)
            self.appBar.pop()
            return 1                            

        self.appBar.pop()        
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
        
        self.appBar.push(_("Saving Configuration..."))
        self.appBar.refresh()
        self.saveHardware()
        self.saveDevices()
        self.saveProfiles()
        self.appBar.pop()
        self.checkApply()        
        return 0

    def saveDevices(self):
        self.appBar.push(_("Saving Device Configuration..."))
        devicelist = getDeviceList()
        devicelist.save()
        devicelist.setChanged(false)
        self.appBar.pop()
        
    def saveHardware(self):
        self.appBar.push(_("Saving Hardware Configuration..."))
        hardwarelist = getHardwareList()
        hardwarelist.save()
        hardwarelist.setChanged(false)
        self.appBar.pop()
        
    def saveProfiles(self):
        self.appBar.push(_("Saving Profile Configuration..."))
        profilelist = getProfileList()
        profilelist.save()
        profilelist.setChanged(false)
        self.appBar.pop()
        
    def hydrate(self):
        self.hydrateProfiles()
        self.hydrateDevices()
        self.hydrateHardware()

    def checkApply(self, ch = -1):
        if ch == -1:
            ch = self.changed()
        apply_btn = self.xml.get_widget("save")
        if ch:
            apply_btn.set_sensitive (TRUE)
        else:
            apply_btn.set_sensitive (FALSE)
            
            
    def hydrateDevices(self):
        self.appBar.push(_("Updating Devices..."))
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
            clist.set_pixmap(row, PROFILE_COLUMN, self.inact_xpm,
                             self.inact_mask)
            clist.set_pixtext(row, STATUS_COLUMN, status, 5, status_pixmap,
                              status_mask)
            clist.set_pixtext(row, DEVICE_COLUMN, devname, 5, device_pixmap,
                              device_mask)
            clist.set_row_data(row, dev)
            
            for prof in profilelist:
                if (prof.Active == true or prof.ProfileName == 'default') and \
                       dev.DeviceId in prof.ActiveDevices:
                    clist.set_pixmap(row, PROFILE_COLUMN,
                                     self.act_xpm, self.act_mask)
                    break
                

            if dev == devsel:
                clist.select_row(row, 0)
                
            row = row + 1
        self.appBar.pop()
        self.checkApply()
        
    def hydrateHardware(self):
        self.appBar.push(_("Updating Hardware..."))
        hardwarelist = getHardwareList()
        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        clist.set_row_height(17)
        for hw in hardwarelist:
            clist.append([str(hw.Description), str(hw.Type), str(hw.Name)])
        self.appBar.pop()
        self.checkApply()

    def hydrateProfiles(self):
        self.appBar.push(_("Updating Profiles..."))
        profilelist = getProfileList()

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
            if prof.DNS.SearchList:
                self.xml.get_widget('searchDnsEntry').set_text(\
                    string.join(prof.DNS.SearchList))
                
            for host in prof.HostsList:
                hclist.append([host.IP, host.Hostname,
                               string.join(host.AliasList, ' ')])
            break

            
        if self.initialized:
            self.appBar.pop()
            self.checkApply()
            return

        self.initialized = true

        self.no_profileentry_update = true
        omenu = self.xml.get_widget('profileMenu')
        omenu = omenu.get_submenu()
        clist = omenu.get_children()
        for child in clist[5:]:
            omenu.remove(child)
            
        history = 0
        i = 0
        group = None
        for prof in profilelist:
            name = prof.ProfileName
            # change the default profile to a more understandable name
            if name == "default":
                name = DEFAULT_PROFILE_NAME
            menu_item = gtk.RadioMenuItem ( group, label = name )
            if not group:
                group = menu_item
            menu_item.show ()
            menu_item.connect ("activate",
                               self.on_profileMenuItem_activated,
                               prof.ProfileName)
            omenu.append (menu_item)
            if prof.ProfileName == self.get_active_profile().ProfileName:
                history = i
            i = i+1
	#omenu.set_history (history)
        omenu.get_children()[history+5].set_active(true)
        self.no_profileentry_update = false
        self.appBar.pop()
        self.checkApply()

    def on_Dialog_delete_event(self, *args):
        if self.changed():        
            button = generic_yesno_dialog(
                _("Do you want to save your changes?"),
                self.dialog)
            if button == RESPONSE_YES:
                self.save()
            
        gtk.mainquit()
        return
    
    def on_mainNotebook_switch_page(self, page = None, a = None,
                                    page_num = 0, *args):
        self.active_page = page_num

        # Check if we aren't called in a dialog destroy event
        if self.xml.get_widget ("addButton") == None:
            return
        
        self.xml.get_widget ("addButton").set_sensitive(false)
        self.xml.get_widget ("editButton").set_sensitive(false)
        self.xml.get_widget ("copyButton").set_sensitive(false)
        self.xml.get_widget ("deleteButton").set_sensitive(false)
        self.xml.get_widget ("commonDockitem").hide()
        self.xml.get_widget ("deviceDockitem").hide()
        self.xml.get_widget ("posDockitem").hide()
        
        if page_num == self.page_num[PAGE_DEVICES]:                        
            self.xml.get_widget ("addButton").set_sensitive(true)
            self.xml.get_widget ("editButton").set_sensitive(true)
            self.xml.get_widget ("copyButton").set_sensitive(true)
            self.xml.get_widget ("deleteButton").set_sensitive(true)
            self.xml.get_widget ("commonDockitem").show()
            self.xml.get_widget ("deviceDockitem").show()
                                
        elif page_num == self.page_num[PAGE_HARDWARE]:
            self.xml.get_widget ("addButton").set_sensitive(true)
            self.xml.get_widget ("editButton").set_sensitive(true)
            self.xml.get_widget ("deleteButton").set_sensitive(true)
            self.xml.get_widget ("commonDockitem").show()
                
        elif page_num == self.page_num[PAGE_HOSTS]:
            self.xml.get_widget ("addButton").set_sensitive(true)
            self.xml.get_widget ("editButton").set_sensitive(true)
            self.xml.get_widget ("deleteButton").set_sensitive(true)
            self.xml.get_widget ("commonDockitem").show()

        elif page_num == self.page_num[PAGE_DNS]:
            self.xml.get_widget ("commonDockitem").show()

    def on_addButton_clicked (self, button):
        self.addButtonFunc[self.active_page](button)
        
    def on_editButton_clicked (self, button):
        self.editButtonFunc[self.active_page](button)

    def on_copyButton_clicked (self, button):
        self.copyButtonFunc[self.active_page](button)

    def on_deleteButton_clicked (self, button):
        self.deleteButtonFunc[self.active_page](button)
        
    def on_upButton_clicked (self, button):
        pass
        
    def on_downButton_clicked (self, button):
        pass
        
    def on_applyButton_clicked (self, button):
        if self.save() == 0:
            generic_info_dialog (_("Changes are saved.\n"
                                    "You may want to restart\n"
                                    "the network and network services\n"
                                    "or restart the computer."),
                                  self.dialog)

    def on_okButton_clicked (self, *args):
        if self.changed():        
            button = generic_yesnocancel_dialog(
                _("Do you want to save your changes?"),
                self.dialog)
            
            if button == RESPONSE_CANCEL:
                return

            if button == RESPONSE_YES:
                if self.save() != 0:
                    return
                else:
                    generic_info_dialog (_("Changes are saved.\n"
                                           "You may want to restart\n"
                                           "the network and network services\n"
                                           "or restart the computer."),
                                         self.dialog)
                                
        gtk.mainquit()
        return
    
    def on_helpButton_clicked(self, button):
        import gnome
        gnome.url_show("ghelp://" + NETCONFDIR + \
                       "/help/index.html")

    def on_deviceAddButton_clicked (self, clicked):
        interface = NewInterfaceDialog(self.dialog)
        
        gtk.mainloop()            
            
        if not interface.canceled:
            self.hydrateDevices()
            self.hydrateHardware()

        return (not interface.canceled)
        
    def on_deviceCopyButton_clicked (self, button):
        devicelist = getDeviceList()

        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        srcdev = clist.get_row_data(clist.selection[0])
        df = NCDeviceFactory.getDeviceFactory()        
        device = df.getDeviceClass(srcdev.Type, srcdev.SubType)()
        device.apply(srcdev)

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

        devicelist.append(device)
        device.commit()
        self.hydrateDevices()

    def on_deviceEditButton_clicked (self, *args):
        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        device = clist.get_row_data(clist.selection[0])

        if device.Type == LO:
            generic_error_dialog (_('The Loopback device can not be edited!'),
                                  self.dialog)
            return

        self.appBar.push(_("Edit Device..."))
        devId = device.DeviceId
        button = self.editDevice(device)

        if button != gtk.RESPONSE_OK and button != 0:
            device.rollback()
            self.appBar.pop()
            return

        device.commit()

        if not device.modified():
            self.appBar.pop()
            return

        # Fixed change device names in active list of all profiles
        profilelist = getProfileList()
        for prof in profilelist:
            if devId in prof.ActiveDevices:
                pos = prof.ActiveDevices.index(devId)
                prof.ActiveDevices[pos] = device.DeviceId
                prof.commit()

        self.hydrateDevices()
        device.changed = false
        self.appBar.pop()

    def editDevice(self, device):
        button = 0
        dialog = device.getDialog()
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
            generic_error_dialog (_('The Loopback device can not be removed!'),
                                  self.dialog)
            return

        buttons = generic_yesno_dialog((_('Do you really want to '
                                          'delete device "%s"?')) % \
                                       str(device.DeviceId),
                                       self.dialog,
                                       widget = clist,
                                       page = clist.selection[0])

        if buttons != RESPONSE_YES:
            return

        for prof in profilelist:
            if device.DeviceId in prof.ActiveDevices:
                pos = prof.ActiveDevices.index(device.DeviceId)
                del prof.ActiveDevices[pos]
        profilelist.commit()
        
        del devicelist[devicelist.index(device)]
        devicelist.commit()
        self.hydrateDevices()

    def on_deviceActivateButton_clicked(self, button):
        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return
        
        dev = clist.get_row_data(clist.selection[0])
        device = dev.getDeviceAlias()

        timeout_remove(self.tag)
        
        if dev.changed:
            button = generic_yesno_dialog(
                _("You have made some changes in your configuration.") + "\n"+\
                _("To activate the network device %s, "
                  "the changes have to be saved.") % (device) + "\n\n" +\
                _("Do you want to continue?"),
                self.dialog)
                
            if button == RESPONSE_YES:
                if self.save() != 0:
                    return
            
            if button == RESPONSE_NO:
                return

        intf = Interface()
        dlg = gtk.Dialog(_('Network device activating...'))
        dlg.set_border_width(10)
        dlg.vbox.add(gtk.Label(_('Activating network device %s, '
                                 'please wait...') %(device)))
        dlg.vbox.show()
        dlg.set_transient_for(self.dialog)        
        dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dlg.set_modal(TRUE)
        dlg.show_all()
        (status, txt) = intf.activate(device)                
        dlg.destroy()
        
        if status != 0:
            generic_longinfo_dialog(_('Cannot activate network device %s\n') %\
                                    (device), txt, self.dialog)

        if NetworkDevice().find(device):
            self.update_devicelist()

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
        generic_error_dialog(_("To be rewritten!"), self.dialog)
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
    
    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_profileMenuItem_activated(self, menu_item, profile):
        if not menu_item.active:
            return
        
        profilelist = getProfileList()
        devicelist = getDeviceList()
        hardwarelist = getHardwareList()

        dosave = false

        for prof in profilelist:
            if prof.Active: break
        else:
            prof = None
        
        if devicelist.modified() or hardwarelist.modified() or \
               (prof and prof.modified()):
            button = generic_yesnocancel_dialog(
                _("Do you want to save your changes?"),
                self.dialog)
            
            if button == RESPONSE_YES:
                dosave = true
            
            if button == RESPONSE_CANCEL:
                return

        if profile == 'default':
            self.xml.get_widget ('profileRenameMenu').set_sensitive (FALSE)
            self.xml.get_widget ('profileDeleteMenu').set_sensitive (FALSE)
        else:
            self.xml.get_widget ('profileRenameMenu').set_sensitive (TRUE)
            self.xml.get_widget ('profileDeleteMenu').set_sensitive (TRUE)
            
        if not self.no_profileentry_update:
            for prof in profilelist:
                if prof.ProfileName == profile:
                    prof.Active = true
                else: prof.Active = false
                prof.commit()
            self.hydrate()
            
        if dosave:
            self.save()

    def on_generic_clist_select_row(self, clist, row, column, event,
                                    edit_button = None, delete_button = None,
                                    copy_button = None, rename_button = None,
                                    up_button = None, down_button = None,
                                    activate_button = None,
                                    deactivate_button = None,
                                    monitor_button = None):
        #devicelist = getDeviceList()

        if edit_button: edit_button.set_sensitive(TRUE)
        if rename_button: rename_button.set_sensitive(TRUE)
        if delete_button: delete_button.set_sensitive(TRUE)
        if copy_button: copy_button.set_sensitive(TRUE)
        if up_button: up_button.set_sensitive(TRUE)
        if down_button: down_button.set_sensitive(TRUE)

        if clist.get_name() == 'deviceList':
            if len(clist.selection) == 0:
                return
            
            curr_prof = self.get_active_profile()
            self.devsel = clist.get_row_data(clist.selection[0])
            
            status = self.clist_get_status()

            if status == ACTIVE and \
                   (self.devsel.DeviceId in curr_prof.ActiveDevices):
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
                     generic_error_dialog (_('The Loopback device '
                                             'can not be disabled!'),
                                           self.dialog)
                     return

                 curr_prof = self.get_active_profile()

                 if device.DeviceId not in curr_prof.ActiveDevices:
                     xpm, mask = self.act_xpm, self.act_mask
                     curr_prof = self.get_active_profile()
                     if curr_prof.ProfileName == 'default':
                         for prof in profilelist:
                             profilelist.activateDevice(name,
                                                        prof.ProfileName, true)
                     else:
                         profilelist.activateDevice(name,
                                                    curr_prof.ProfileName,
                                                    true)
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
                             profilelist.activateDevice(name, prof.ProfileName,
                                                        false)
                     else:
                         profilelist.activateDevice(name,
                                                    curr_prof.ProfileName,
                                                    false)
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
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.Active == true:
                s = entry.get_text()
                prof.DNS.SearchList = prof.DNS.SearchList[:0]
                for sp in string.split(s):
                    prof.DNS.SearchList.append(sp)
                prof.DNS.commit()
                break
        self.checkApply()
            
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
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        button = dl.run ()
        dl.destroy()
        if button != gtk.RESPONSE_OK and button != 0:
            return
        
        i = hostslist.addHost()
        hostslist[i].apply(host)
        hostslist[i].commit()
        self.hydrateProfiles()

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
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        button = dl.run ()
        dl.destroy()
        if button != gtk.RESPONSE_OK and button != 0:
            host.rollback()
            return
        host.commit()
        if host.changed:
            self.hydrateProfiles()
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
        self.hydrateProfiles()

    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_profileAddMenu_activate (self, *args):
        dialog = self.xml.get_widget("ProfileNameDialog")
        dialog.set_transient_for(self.dialog)
        self.xml.get_widget("ProfileName").set_text('')
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
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
            generic_error_dialog (_('The name may only contain '
                                    'letters and digits!'), self.dialog)
            return 1

        if text == 'default' or text == DEFAULT_PROFILE_NAME:
            generic_error_dialog (_('The profile can\'t be named "%s"!') \
                                  % text, self.dialog)
            return 1

        for prof in profilelist:
            if prof.ProfileName == text:
                generic_error_dialog (_('The profile name already exists!'),
                                      self.dialog)
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
        self.hydrateProfiles()
        return 0

    def on_profileCopyMenu_activate (self, *args):
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
        self.hydrateProfiles()

    def on_profileRenameMenu_activate (self, *args):
        profilelist = getProfileList()
        
        profile = self.get_active_profile()
        if profile.ProfileName == 'default':
            generic_error_dialog (_('The "%s" profile can\'t be renamed!') \
                                  % DEFAULT_PROFILE_NAME,
                                  self.dialog)
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
            generic_error_dialog (_('The name may only contain '
                                    'letters and digits!'), self.dialog)
            return

        if text == 'default' or text == DEFAULT_PROFILE_NAME:
            generic_error_dialog (_('The profile can\'t be named "%s"!') % \
                                  text, self.dialog)
            return

        for prof in profilelist:
            if prof.ProfileName == text and prof != profile:
                generic_error_dialog (_('The profile name already exists!'),
                                      self.dialog)
                return

        profile.ProfileName = text
        profile.commit()        
        self.initialized = None
        if profile.changed:
            self.hydrateProfiles()
            profile.changed = false

    def on_profileDeleteMenu_activate (self, *args):
        profilelist = getProfileList()

        #clist = self.xml.get_widget('profileList')

        #if len(clist.selection) == 0:
        #    return

        name = self.get_active_profile().ProfileName

        if name == 'default':
            generic_error_dialog(_('The "%s" Profile '
                                   'can not be deleted!') \
                                 % DEFAULT_PROFILE_NAME,
                                 self.dialog)
            return

        buttons = generic_yesno_dialog((_('Do you really want to '
                                          'delete profile "%s"?')) % str(name),
                                       self.dialog)

        if buttons != RESPONSE_YES:
            return

        del profilelist[profilelist.index(self.get_active_profile())]
        profilelist.commit()
        profilelist[0].Active = true
        self.initialized = None
        #clist.clear()
        self.hydrate()

    def on_hardwareAddButton_clicked (self, *args):
        type = hardwareTypeDialog()
        dialog = type.xml.get_widget ("Dialog")
        dialog.set_transient_for(self.dialog)
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        button = dialog.run ()
        dialog.destroy()

        if button != gtk.RESPONSE_OK and button != 0:
            return

        hardwarelist = getHardwareList()

        type = type.type
        i = hardwarelist.addHardware(type)
        hw = hardwarelist[i]
        
        if self.showHardwareDialog(hw) == gtk.RESPONSE_OK:
            hw.commit()
            hardwarelist.commit()
            self.hydrateHardware()
        else:
            hardwarelist.remove(hw)

    def on_hardwareEditButton_clicked (self, *args):
        clist = self.xml.get_widget('hardwareList')

        if len(clist.selection) == 0:
            return

        type  = clist.get_text(clist.selection[0], 1)
        hardwarelist = getHardwareList()
        hw = hardwarelist[clist.selection[0]]

        if self.showHardwareDialog(hw) == gtk.RESPONSE_OK:
            hw.commit()
            hardwarelist.commit()
        else:
            hw.rollback()

    def showHardwareDialog(self, hw = None):
        dl = None
        if hw:
            dl = hw.getDialog()

        if dl:
            dl.set_transient_for(self.dialog)
            button = dl.run()
            dl.destroy()                    
            
            return button
    
        else:
            generic_error_dialog (_("Sorry, there is nothing to be edited,\n"
                                    "or this type cannot be edited yet."),
                                  self.dialog)
            return RESPONSE_CANCEL                    

    def on_hardwareDeleteButton_clicked (self, *args):
        hardwarelist = getHardwareList()

        clist = self.xml.get_widget("hardwareList")

        if len(clist.selection) == 0:
            return

        hw = hardwarelist[clist.selection[0]]
        description = clist.get_text(clist.selection[0], 0)
        type = clist.get_text(clist.selection[0], 1)
        dev = clist.get_text(clist.selection[0], 2)

        buttons = generic_yesno_dialog((_('Do you really '
                                          'want to delete "%s"?')) % \
                                       str(description),
                                       self.dialog, widget = clist,
                                       page = clist.selection[0])

        if buttons != RESPONSE_YES:
            return

        # remove hardware
        del hardwarelist[clist.selection[0]]
        hardwarelist.commit()
        self.hydrateHardware()

        buttons = generic_yesno_dialog((_('Do you want to delete '
                                          'all devices that used "%s"?')) % \
                                       str(description),
                                       self.dialog, widget = clist,
                                       page = clist.selection[0])

        if buttons == RESPONSE_YES:
            # remove all devices used this hardware
            #
            # FIXME!! This has to be modular, not hardcoded!
            #
            devicelist = getDeviceList()
            profilelist = getProfileList()
            dlist = []
            for d in devicelist:
                found = FALSE
                if type == MODEM:
                    if d.Dialup and d.Dialup.Inherits and \
                           dev == d.Dialup.Inherits:
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
            self.hydrateDevices()


    def on_about_activate(self, *args):
        dlg = gnome.ui.About(PROGNAME,
                             netconfpkg.PRG_VERSION,
                             _("Copyright (c) 2001,2002 Red Hat, Inc."),
                             _("This software is distributed under the GPL. "
                               "Please Report bugs to Red Hat's Bug Tracking "
                               "System: http://bugzilla.redhat.com/"),
                             ["Harald Hoyer <harald@redhat.com>",
                              "Than Ngo <than@redhat.com>",
                              "Philipp Knirsch <pknirsch@redhat.com>",
                              unicode("Trond Eivind Glomsrød <teg@redhat.com>",
                                      "iso8859-1")])
        
        dlg.set_transient_for(self.dialog)
        dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dlg.show()


