#!/usr/bin/python2.2

## netconf - A network configuration tool
## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>
## Copyright (C) 2001, 2002 Trond Eivind Glomsrød <teg@redhat.com>
## Copyright (C) 2001 - 2003 Harald Hoyer <harald@redhat.com>

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
from netconfpkg.gui.GUI_functions import *
from netconfpkg.gui.NewInterfaceDialog import NewInterfaceDialog
from netconfpkg.gui.edithosts import editHostsDialog
import gtk
import gtk.glade
import gnome.ui
import gnome

PROFILE_COLUMN = 0
STATUS_COLUMN = 1
DEVICE_COLUMN = 2
NICKNAME_COLUMN = 3
TYPE_COLUMN = 4

TRUE=gtk.TRUE
FALSE=gtk.FALSE

PAGE_DEVICES = 0
PAGE_HARDWARE = 1
PAGE_IPSEC = 2
PAGE_DNS = 3
PAGE_HOSTS = 4
    
class mainDialog:
    def __init__(self):
        glade_file = "maindialog.glade"

        if not os.path.isfile(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=PROGNAME)
        self.initialized = None
        self.no_profileentry_update = None


        self.edit_button = self.xml.get_widget("editButton")
        self.delete_button = self.xml.get_widget("deleteButton")
        self.copy_button = self.xml.get_widget("copyButton")
        self.activate_button = self.xml.get_widget("activateButton")
        self.deactivate_button = self.xml.get_widget("deactivateButton")
        self.monitor_button = self.xml.get_widget("deviceMonitorButton")
        self.up_button = self.xml.get_widget("upButton")
        self.down_button = self.xml.get_widget("downButton")

        xml_signal_autoconnect(self.xml,
            {
            "on_activateButton_clicked" : \
            self.on_activateButton_clicked,
            "on_deactivateButton_clicked" : \
            self.on_deactivateButton_clicked,
            "on_deviceMonitorButton_clicked" : \
            self.on_deviceMonitorButton_clicked,
            "on_deviceList_select_row" : 
            self.on_generic_clist_select_row,
            "on_deviceList_unselect_row" : 
            self.on_generic_clist_unselect_row,
            "on_deviceList_button_press_event" : \
            self.on_generic_clist_button_press_event,
            "on_save_activate" : self.on_applyButton_clicked,
            "on_quit_activate" : self.on_okButton_clicked,
            "on_contents_activate" : self.on_helpButton_clicked,
            "on_hardwareList_select_row" :
            self.on_generic_clist_select_row,
            "on_hardwareList_unselect_row" : 
            self.on_generic_clist_unselect_row,
            "on_hardwareList_button_press_event" : \
            self.on_generic_clist_button_press_event,
            "on_ipsecList_button_press_event" : \
            self.on_generic_clist_button_press_event,
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
        self.dialog.set_position (gtk.WIN_POS_CENTER)
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
        self.hwsel = None
        self.ipsel = None
        self.active_profile_name = DEFAULT_PROFILE_NAME
        
#         clist = self.xml.get_widget("hardwareList")
#         # First: copy the clist-style
#         self.style1 = clist.get_style().copy()
#         self.style2 = clist.get_style().copy()
#         self.style3 = clist.get_style().copy()
#         color1 = "lightgreen"
#         color2 = "light salmon"
#         color3 = "white"
#         colormap = clist.get_colormap()
#         self.style1.base[gtk.STATE_NORMAL] = colormap.alloc_color(color1)
#         self.style2.base[gtk.STATE_NORMAL] = colormap.alloc_color(color2)
#         self.style3.base[gtk.STATE_NORMAL] = colormap.alloc_color(color3)

        if not os.access('/usr/bin/rp3', os.X_OK):
            self.xml.get_widget('deviceMonitorButton').hide()
        
        load_icon("network.xpm", self.dialog)
        
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
            PAGE_IPSEC : notebook.page_num(\
            self.xml.get_widget('ipsecFrame')),
            PAGE_HOSTS : notebook.page_num(\
            self.xml.get_widget('hostFrame')),
            PAGE_DNS : notebook.page_num(\
            self.xml.get_widget('dnsFrame')),
            }

        self.active_page = self.page_num[PAGE_DEVICES]
        
        self.addButtonFunc = {
            PAGE_DEVICES : self.on_deviceAddButton_clicked,
            PAGE_HARDWARE : self.on_hardwareAddButton_clicked,
            PAGE_IPSEC : self.on_ipsecAddButton_clicked,
            PAGE_HOSTS : self.on_hostsAddButton_clicked,
            }

        self.activateButtonFunc = {
            PAGE_DEVICES : self.on_deviceActivateButton_clicked,
            PAGE_HARDWARE : self.nop,
            PAGE_IPSEC : self.on_ipsecActivateButton_clicked,
            PAGE_HOSTS : self.nop,
            }

        self.deactivateButtonFunc = {
            PAGE_DEVICES : self.on_deviceDeactivateButton_clicked,
            PAGE_HARDWARE : self.nop,
            PAGE_IPSEC : self.on_ipsecDeactivateButton_clicked,
            PAGE_HOSTS : self.nop,
            }

        self.editButtonFunc = {
            PAGE_DEVICES : self.on_deviceEditButton_clicked,
            PAGE_HARDWARE : self.on_hardwareEditButton_clicked,
            PAGE_IPSEC : self.on_ipsecEditButton_clicked,
            PAGE_HOSTS : self.on_hostsEditButton_clicked,
            }

        self.copyButtonFunc = {
            PAGE_DEVICES : self.on_deviceCopyButton_clicked,
            PAGE_HARDWARE : self.nop,
            PAGE_IPSEC : self.nop,
            PAGE_HOSTS : self.nop,
            }

        self.deleteButtonFunc = {
            PAGE_DEVICES : self.on_deviceDeleteButton_clicked,
            PAGE_HARDWARE : self.on_hardwareDeleteButton_clicked,
            PAGE_IPSEC : self.on_ipsecDeleteButton_clicked,
            PAGE_HOSTS : self.on_hostsDeleteButton_clicked,
            }

        self.editMap = {
            "deviceList" : PAGE_DEVICES,
            "hardwareList" : PAGE_HARDWARE,
            "ipsecList" : PAGE_IPSEC,
            }
        
        self.load()
        self.hydrate()

        self.activedevicelist = NetworkDevice().get()
        self.tag = gtk.timeout_add(4000, self.updateDevicelist)
                
        # initialize the button state..
        clist = self.xml.get_widget("deviceList")
        self.on_generic_clist_select_row(\
            clist, 0, 0, 0)
        
        gtk.Tooltips().enable()

        self.dialog.show()
        
        self.on_mainNotebook_switch_page(None, None,
                                         self.page_num[PAGE_DEVICES])

##         for col in [ PROFILE_COLUMN, STATUS_COLUMN, DEVICE_COLUMN,
##                      NICKNAME_COLUMN, TYPE_COLUMN ]:
##             colsize = clist.optimal_column_width(col) + 5
##             titlesize = clist.get_column_widget(col)
##             print titlesize.get_children()[0].get_width()
##             #clist.set_column_width(col, )

        

    def nop(self, *args):
        pass

    def load(self):
        self.appBar.push(_("Loading configuration..."))
        self.loadDevices()
        self.loadHardware()
        self.loadProfiles()
        self.loadIPsec()
        self.appBar.pop()

    def loadDevices(self):
        self.appBar.push(_("Loading device configuration..."))
        devicelist = getDeviceList()
        self.appBar.pop()
        
    def loadHardware(self):
        self.appBar.push(_("Loading hardware configuration..."))
        hardwarelist = getHardwareList()
        self.appBar.pop()

    def loadProfiles(self):
        self.appBar.push(_("Loading profile configuration..."))
        profilelist = getProfileList()
        self.appBar.pop()
    
    def loadIPsec(self):
        self.appBar.push(_("Loading IPsec configuration..."))
        ipseclist = getIPsecList()
        self.appBar.pop()
    
    def test(self):
        self.appBar.push(_("Testing configuration set..."))
        profilelist = getProfileList()
        devicelist = getDeviceList()
        hardwarelist = getHardwareList()
        ipseclist = getIPsecList()
        try:
            hardwarelist.test()
            devicelist.test()
            profilelist.test()
            ipseclist.test()
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
        ipseclist = getIPsecList()
        self.appBar.pop()

        profname = self.active_profile_name
        
        if profilelist.modified() \
               or devicelist.modified() \
               or hardwarelist.modified() \
               or ipseclist.modified():
            self.appBar.push(_("Active profile: %s (modified)") % \
                             self.active_profile_name)
            return true

        self.appBar.push(_("Active profile: %s")% profname)

        return false

    def save(self):
        if self.test() != 0:
            return 1
        
        self.appBar.push(_("Saving configuration..."))
        self.appBar.refresh()
        profilelist = getProfileList()
        try:
            profilelist.fixInterfaces()
            self.saveHardware()
            self.saveDevices()
            self.saveIPsecs()
            self.saveProfiles()
            self.appBar.pop()
            self.checkApply()     
	except (IOError, OSError, EnvironmentError), errstr:
            generic_error_dialog (_("Error saving configuration!\n%s") \
                                  % (str(errstr)))
        else:
            generic_info_dialog (_("Changes are saved.\n"
                                   "You may want to restart\n"
                                   "the network and network services\n"
                                   "or restart the computer."),
                                 self.dialog)
        self.appBar.pop()
        return 0

    def saveDevices(self):
        self.appBar.push(_("Saving device configuration..."))
        devicelist = getDeviceList()
        devicelist.save()
        devicelist.setChanged(false)
        self.appBar.pop()
        
    def saveHardware(self):
        self.appBar.push(_("Saving hardware configuration..."))
        hardwarelist = getHardwareList()
        hardwarelist.save()
        hardwarelist.setChanged(false)
        self.appBar.pop()
        
    def saveProfiles(self):
        self.appBar.push(_("Saving profile configuration..."))
        profilelist = getProfileList()
        profilelist.save()
        profilelist.setChanged(false)
        self.appBar.pop()

    def saveIPsecs(self):
        self.appBar.push(_("Saving IPsec configuration..."))
        ipseclist = getIPsecList()
        ipseclist.save()
        ipseclist.setChanged(false)
        self.appBar.pop()
        
    def hydrate(self):
        self.hydrateProfiles()
        self.hydrateDevices()
        self.hydrateHardware()
        self.hydrateIPsec()

    def checkApply(self, ch = -1):
        if ch == -1:
            ch = self.changed()
        apply_btn = self.xml.get_widget("save")
        if ch:
            apply_btn.set_sensitive (TRUE)
        else:
            apply_btn.set_sensitive (FALSE)
            
            
    def hydrateDevices(self):
        self.appBar.push(_("Updating devices..."))
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
                get_device_icon_mask(dev.Type, self.dialog)

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
                log.log(5, "Selecting row %d" % row)
                clist.select_row(row, 0)
                
            row = row + 1
        self.appBar.pop()
        self.checkApply()
        
    def hydrateHardware(self):
        self.appBar.push(_("Updating hardware..."))
        hardwarelist = getHardwareList()
        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        clist.set_row_height(17)
        row = 0
        hwsel = self.hwsel

        for hw in hardwarelist:
            clist.append([str(hw.Description), str(hw.Type), str(hw.Name), str(hw.Status)])
            device_pixmap, device_mask = \
                get_device_icon_mask(hw.Type, self.dialog)
            clist.set_pixtext(row, DEVICE_COLUMN, hw.Name, 5,
                              device_pixmap,
                              device_mask)
            clist.set_row_data(row, hw)

            if hw == hwsel:
                log.log(5, "Selecting row %d" % row)
                clist.select_row(row, 0)

#             if hw.Status == HW_OK:
#                 clist.set_row_style(row, self.style1)
#             elif hw.Status == HW_CONF:
#                 clist.set_row_style(row, self.style3)
#             else:
#                 clist.set_row_style(row, self.style2)
                
            row += 1
        self.appBar.pop()
        self.checkApply()

    def hydrateIPsec(self):
        ipseclist = getIPsecList()
        clist = self.xml.get_widget("ipsecList")
        clist.clear()
        clist.set_row_height(17)
        row = 0
        ipsel = self.ipsel
        profilelist = getProfileList()

        status = ACTIVE
        status_pixmap = self.on_xpm
        status_mask = self.on_mask

        for ipsec in ipseclist:
#             if ipsec.IPsecId in profilelist.ActiveIPsecs:
#                 status = ACTIVE
#                 status_pixmap = self.on_xpm
#                 status_mask = self.on_mask
#             else:
#                 status = INACTIVE
#                 status_pixmap = self.off_xpm
#                 status_mask = self.off_mask

            clist.append(['', str(ipsec.ConnectionType),
                          str(ipsec.RemoteIPAddress),
                          str(ipsec.IPsecId)])
            
            clist.set_pixmap(row, PROFILE_COLUMN, self.inact_xpm,
                             self.inact_mask)
            clist.set_row_data(row, ipsec)
            
            for prof in profilelist:
                if (prof.Active == true or prof.ProfileName == 'default') and \
                       ipsec.IPsecId in prof.ActiveIPsecs:
                    clist.set_pixmap(row, PROFILE_COLUMN,
                                     self.act_xpm, self.act_mask)
                    break
                

            if ipsec == ipsel:
                log.log(5, "Selecting row %d" % row)
                clist.select_row(row, 0)
                
            row += 1
        self.appBar.pop()
        self.checkApply()


#         if device.IPsecList != None:
#             for ipsec in device.IPsecList:            
#                 clist.append([ipsec.RemoteIPAddress or "-",
#                               (ipsec.ConnectionType == "Net2Net" and ipsec.RemoteNetwork) or "-",
#                               (ipsec.ConnectionType == "Net2Net" and ipsec.LocalNetwork) or "-",
#                               ])
#         else:
#             device.createIPsecList()

    def getActiveProfile(self):
        #print "getActiveProfile == %s " % self.active_profile.ProfileName
        return self.active_profile

    def hydrateProfiles(self):
        self.appBar.push(_("Updating profiles..."))
        profilelist = getProfileList()

        hclist = self.xml.get_widget("hostsList")
        hclist.clear()
        hclist.set_row_height(17)

        for prof in profilelist:
            if not prof.Active:
                continue

            name = prof.ProfileName            
            if name == "default":
                name = DEFAULT_PROFILE_NAME
            self.active_profile_name = name
            break
        else:
            prof = profilelist[0]

        #print "hydrateProfiles(%s)" % self.active_profile_name
        self.active_profile = prof
        
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
        else:
            self.xml.get_widget('searchDnsEntry').set_text('')

        row = 0
        for host in prof.HostsList:
            #88357
            if host.IP == "127.0.0.1":
                continue
            hclist.append([host.IP, host.Hostname,
                           string.join(host.AliasList, ' ')])
            hclist.set_row_data(row, host)
            row += 1
            
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
            if prof.Active:
                menu_item.set_active(true)
            menu_item.connect ("activate",
                               self.on_profileMenuItem_activated,
                               prof.ProfileName)
            omenu.append (menu_item)
	#omenu.set_history (history)
        self.no_profileentry_update = false
        self.appBar.pop()
        self.checkApply()

    def updateDevicelist(self):
        activedevicelistold = self.activedevicelist
        self.activedevicelist = NetworkDevice().get()

        if activedevicelistold != self.activedevicelist:
            self.hydrateDevices()
            return TRUE

        return TRUE
    
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
            clist = self.xml.get_widget("deviceList")
            self.xml.get_widget ("addButton").set_sensitive(true)
            self.xml.get_widget ("editButton").set_sensitive(true)
            self.xml.get_widget ("copyButton").set_sensitive(true)
            self.xml.get_widget ("deleteButton").set_sensitive(true)
            self.xml.get_widget ("commonDockitem").show()
            self.xml.get_widget ("deviceDockitem").show()
                                
        elif page_num == self.page_num[PAGE_HARDWARE]:
            clist = self.xml.get_widget("hardwareList")
            self.xml.get_widget ("addButton").set_sensitive(true)
            self.xml.get_widget ("editButton").set_sensitive(true)
            self.xml.get_widget ("deleteButton").set_sensitive(true)
            self.xml.get_widget ("commonDockitem").show()
                
        elif page_num == self.page_num[PAGE_IPSEC]:
            clist = self.xml.get_widget("ipsecList")
            self.xml.get_widget ("addButton").set_sensitive(true)
            self.xml.get_widget ("editButton").set_sensitive(true)
            self.xml.get_widget ("deleteButton").set_sensitive(true)
            self.xml.get_widget ("commonDockitem").show()
            self.xml.get_widget ("deviceDockitem").show()
                
        elif page_num == self.page_num[PAGE_HOSTS]:
            clist = None
            self.xml.get_widget ("addButton").set_sensitive(true)
            self.xml.get_widget ("editButton").set_sensitive(true)
            self.xml.get_widget ("deleteButton").set_sensitive(true)
            self.xml.get_widget ("commonDockitem").show()

        elif page_num == self.page_num[PAGE_DNS]:
            clist = None
            self.xml.get_widget ("commonDockitem").show()

        if clist:
            self.on_generic_clist_select_row(clist, 0, 0, 0)


    def on_activateButton_clicked (self, button):
        self.activateButtonFunc[self.active_page](button)

    def on_deactivateButton_clicked (self, button):
        self.deactivateButtonFunc[self.active_page](button)

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
        self.save()
        
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
                                
        gtk.mainquit()
        return
    
    def on_helpButton_clicked(self, button):
        import gnome
        gnome.url_show("file:" + NETCONFDIR + \
                       "/help/index.html")        

    def on_deviceAddButton_clicked (self, clicked):
        interface = NewInterfaceDialog(self.dialog)
        gtk.mainloop()            
            
        if not interface.canceled:
            self.hydrateDevices()
            self.hydrateHardware()

        return (not interface.canceled)
        
    def on_deviceCopyButton_clicked (self, button):
        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        srcdev = clist.get_row_data(clist.selection[0])
        df = NCDeviceFactory.getDeviceFactory()        
        device = df.getDeviceClass(srcdev.Type, srcdev.SubType)()
        device.apply(srcdev)

        duplicate = TRUE
        num = 0
        devicelist = getDeviceList()
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

        self.appBar.push(_("Edit device..."))
        devId = device.DeviceId
        button = self.editDevice(device)

        if button != gtk.RESPONSE_OK and button != 0:
            device.rollback()
            self.appBar.pop()
            return

        device.commit()
        devicelist = getDeviceList()
        devicelist.commit()

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
        if dialog:
            dialog.set_transient_for(self.dialog)
            dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            button = dialog.run()
            dialog.destroy()
        else:
            generic_error_dialog (_('The device type %s cannot be edited!\n') \
                                  % device.Type,
                                  self.dialog)
            

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
                                       self.dialog, widget = clist,
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

        gtk.timeout_remove(self.tag)
        
        if self.changed():
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

        (status, txt) = dev.activate(dialog = self.dialog)

        if NetworkDevice().find(device):
            self.updateDevicelist()

        self.tag = gtk.timeout_add(4000, self.updateDevicelist)
            
    def on_deviceDeactivateButton_clicked(self, button):
        clist = self.xml.get_widget("deviceList")
        if len(clist.selection) == 0:
            return

        dev = clist.get_row_data(clist.selection[0])
        device = dev.getDeviceAlias()
        
        if not device:
            return
        
        gtk.timeout_remove(self.tag)

        (status, txt) = dev.deactivate(dialog = self.dialog)
        
        self.updateDevicelist()

        self.tag = gtk.timeout_add(4000, self.updateDevicelist)

    def on_deviceMonitorButton_clicked(self, button):
        generic_error_dialog(_("To be rewritten!"), self.dialog)
        return
    
    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_profileMenuItem_activated(self, menu_item, profile):
        if not menu_item or not menu_item.active:
            return

        #print "on_profileMenuItem_activated(%s)" % profile
        
        profilelist = getProfileList()
        devicelist = getDeviceList()
        hardwarelist = getHardwareList()

        dosave = false

        prof = self.active_profile
        
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
            profilelist.switchToProfile(profile, dochange = false)
            self.initialized = true
            self.hydrate()

        if dosave:
            self.save()

    def on_generic_clist_select_row(self, clist, row, column, event):
        #devicelist = getDeviceList()
        
        self.edit_button.set_sensitive(TRUE)
        self.delete_button.set_sensitive(TRUE)

        if self.active_page == self.page_num[PAGE_DEVICES]:
            self.copy_button.set_sensitive(TRUE)
            #self.rename_button.set_sensitive(TRUE)

        if clist.get_name() == 'hardwareList':
            if len(clist.selection) == 0:
                return
            self.hwsel = clist.get_row_data(clist.selection[0])
            if not self.hwsel:
                return

        if clist.get_name() == 'ipsecList':
            if len(clist.selection) == 0:
                return
            self.ipsel = clist.get_row_data(clist.selection[0])
            if not self.ipsel:
                return

            self.activate_button.set_sensitive(TRUE)
            self.deactivate_button.set_sensitive(TRUE)
            self.delete_button.set_sensitive(TRUE)


        if clist.get_name() == 'deviceList':
            if len(clist.selection) == 0:
                return

            self.devsel = clist.get_row_data(clist.selection[0])
            if not self.devsel:
                return
            
            curr_prof = self.getActiveProfile()
            status = clist.get_pixtext(clist.selection[0], STATUS_COLUMN)[0]
            if NetworkDevice().find(self.devsel.getDeviceAlias()):
                status == ACTIVE
                
            if status == ACTIVE and \
                   (self.devsel.DeviceId in curr_prof.ActiveDevices):
                self.activate_button.set_sensitive(FALSE)
                self.deactivate_button.set_sensitive(TRUE)
                self.delete_button.set_sensitive(FALSE)
                self.monitor_button.set_sensitive(TRUE)
            else:
                self.activate_button.set_sensitive(TRUE)
                self.deactivate_button.set_sensitive(FALSE)
                self.delete_button.set_sensitive(TRUE)
                self.monitor_button.set_sensitive(FALSE)


    def on_generic_clist_unselect_row(self, clist, row, column, event):
        if self.edit_button: self.edit_button.set_sensitive(FALSE)
        #if self.rename_button: self.rename_button.set_sensitive(FALSE)
        if self.delete_button: self.delete_button.set_sensitive(FALSE)
        if self.copy_button: self.copy_button.set_sensitive(FALSE)
        if self.up_button: self.delete_button.set_sensitive(FALSE)
        if self.down_button: self.copy_button.set_sensitive(FALSE)

    def on_generic_clist_button_release_event(self, clist, event, func):
        id = clist.get_data ("signal_id")
        clist.disconnect (id)
        #clist.remove_data ("signal_id")
        apply (func)

    def on_generic_clist_button_press_event(self, clist, event, *args):
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
            if info != None and not (clist.get_name() in \
                                     [ "deviceList", "ipsecList" ] \
                                     and len(info) >= 2 and info[1] == 0):
                func = self.nop
                if self.editMap.has_key(clist.get_name()):
                    func = self.editButtonFunc[self.editMap[clist.get_name()]]
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

                 curr_prof = self.getActiveProfile()

                 if device.DeviceId not in curr_prof.ActiveDevices:
                     xpm, mask = self.act_xpm, self.act_mask
                     curr_prof = self.getActiveProfile()
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

        if clist.get_name() == 'ipsecList' and gtk.gdk.BUTTON_PRESS:
             info = clist.get_selection_info(event.x, event.y)
             if info != None and info[1] == 0:
                 row = info[0]

                 ipsec = clist.get_row_data(row)
                 name = ipsec.IPsecId

                 curr_prof = self.getActiveProfile()

                 if ipsec.IPsecId not in curr_prof.ActiveIPsecs:
                     xpm, mask = self.act_xpm, self.act_mask
                     curr_prof = self.getActiveProfile()
                     if curr_prof.ProfileName == 'default':
                         for prof in profilelist:
                             profilelist.activateIpsec(name,
                                                        prof.ProfileName, true)
                     else:
                         profilelist.activateIpsec(name,
                                                    curr_prof.ProfileName,
                                                    true)
                         for prof in profilelist:
                             if prof.ProfileName == "default":
                                 continue
                             if name not in prof.ActiveIPsecs:
                                 break
                         else:
                             profilelist.activateIpsec(name, 'default', true)
                        
                 else:
                     xpm, mask = self.inact_xpm, self.inact_mask
                     if curr_prof.ProfileName == 'default':
                         for prof in profilelist:
                             profilelist.activateIpsec(name, prof.ProfileName,
                                                        false)
                     else:
                         profilelist.activateIpsec(name,
                                                    curr_prof.ProfileName,
                                                    false)
                         profilelist.activateIpsec(name, 'default', false)

                 for prof in profilelist:
                     prof.commit()
                 
                 clist.set_pixmap(row, PROFILE_COLUMN, xpm, mask)
                 self.checkApply()
                 
    def on_hostnameEntry_changed(self, entry):
        self.active_profile.DNS.Hostname = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()
        
    def on_domainEntry_changed(self, entry):
        self.active_profile.DNS.Domainname = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()
            
    def on_primaryDnsEntry_changed(self, entry):
        self.active_profile.DNS.PrimaryDNS = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()
            
    def on_secondaryDnsEntry_changed(self, entry):
        self.active_profile.DNS.SecondaryDNS = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()
            
    def on_tertiaryDnsEntry_changed(self, entry):
        self.active_profile.DNS.TertiaryDNS = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()
            
    def on_searchDnsEntry_changed(self, entry):
        s = entry.get_text()
        self.active_profile.DNS.SearchList = self.active_profile.\
                                             DNS.SearchList[:0]
        for sp in string.split(s):
            self.active_profile.DNS.SearchList.append(sp)
        self.active_profile.DNS.commit()
        self.checkApply()
            
    def on_hostsAddButton_clicked(self, *args):
        profilelist = getProfileList()

        curr_prof = self.getActiveProfile()
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
        
        i=  hostslist.addHost()
        hostslist[i].apply(host)
        hostslist[i].commit()
        self.hydrateProfiles()

    def on_hostsEditButton_clicked (self, *args):
        profilelist = getProfileList()

        curr_prof = self.getActiveProfile()
        hostslist = curr_prof.HostsList
        clist  = self.xml.get_widget("hostsList")

        if len(clist.selection) == 0:
            return

        host = clist.get_row_data(clist.selection[0])

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
        prof = self.getActiveProfile()

        clist = self.xml.get_widget('hostsList')

        if len(clist.selection) == 0:
            return

        todel = list(clist.selection)
        todel.sort()
        todel.reverse()

        for i in todel:
            prof.HostsList.remove(clist.get_row_data(i))
            
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
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
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
        prof.commit()

        profilelist.switchToProfile(prof, dochange = false)

        #self.xml.get_widget("profileList").clear()
        self.initialized = false
        self.hydrateProfiles()
        return 0

    def on_profileCopyMenu_activate (self, *args):
        profilelist = getProfileList()

        profile = Profile()
        profile.apply(self.getActiveProfile())
        profile.Active = false
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
        
        profile = self.getActiveProfile()
        if profile.ProfileName == 'default' or \
               profile.ProfileName == DEFAULT_PROFILE_NAME:
            generic_error_dialog (_('The "%s" profile can\'t be renamed!') \
                                  % DEFAULT_PROFILE_NAME,
                                  self.dialog)
            return

        dialog = self.xml.get_widget("ProfileNameDialog")
        dialog.set_transient_for(self.dialog)
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
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

        name = self.getActiveProfile().ProfileName

        if name == 'default' or name == DEFAULT_PROFILE_NAME:
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

        del profilelist[profilelist.index(self.getActiveProfile())]
        profilelist.commit()
        profilelist.switchToProfile('default')
        self.initialized = None
        #clist.clear()
        self.hydrate()

    def on_hardwareAddButton_clicked (self, *args):
        from hardwaretype import hardwareTypeDialog
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
        self.hydrateHardware()


    def on_hardwareEditButton_clicked (self, *args):
        clist = self.xml.get_widget('hardwareList')

        if len(clist.selection) == 0:
            return
        
        #type  = clist.get_text(clist.selection[0], 1)
        hardwarelist = getHardwareList()
        #hw = hardwarelist[clist.selection[0]]
        hw = clist.get_row_data(clist.selection[0])
        type = hw.Type
        
        if self.showHardwareDialog(hw) == gtk.RESPONSE_OK:
            hw.commit()
            hardwarelist.commit()
        else:
            hw.rollback()
        self.hydrateHardware()

    def showHardwareDialog(self, hw = None):
        dl = None
        if hw:
            dl = hw.getDialog()

        if dl:
            dl.set_transient_for(self.dialog)
            dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
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

        hw = clist.get_row_data(clist.selection[0])
        type = hw.Type
        description = hw.Description
        dev = hw.Name
        
        buttons = generic_yesno_dialog((_('Do you really '
                                          'want to delete "%s"?')) % \
                                       str(description),
                                       self.dialog, widget = clist,
                                       page = clist.selection[0])

        if buttons != RESPONSE_YES:
            return

        # remove hardware
        hardwarelist.remove(hw)
        hardwarelist.commit()

        buttons = generic_yesno_dialog((_('Do you want to delete '
                                          'all devices that used "%s"?')) % \
                                       str(description),
                                       self.dialog, widget = clist)

        if buttons == RESPONSE_YES:
            # remove all devices that use this hardware
            devicelist = getDeviceList()
            profilelist = getProfileList()
            dlist = []
            for d in devicelist:
                if dev == d.getHWDevice():
                    dlist.append(d)

            for i in dlist:
                for prof in profilelist:
                    if i.DeviceId in prof.ActiveDevices:
                        prof.ActiveDevices.remove(i.DeviceId)
                devicelist.remove(i)

            devicelist.commit()
            self.hydrateDevices()

        self.hydrateHardware()

    def on_about_activate(self, *args):
        from version import PRG_VERSION
        from version import PRG_NAME
        dlg = gnome.ui.About(PRG_NAME,
                             PRG_VERSION,
                             _("Copyright (c) 2001-2003 Red Hat, Inc."),
                             _("This software is distributed under the GPL. "
                               "Please report bugs to Red Hat's bug tracking "
                               "system: http://bugzilla.redhat.com/"),
                             ["Harald Hoyer <harald@redhat.com>",
                              "Than Ngo <than@redhat.com>",
                              "Philipp Knirsch <pknirsch@redhat.com>",
                              "Trond Eivind Glomsrød <teg@redhat.com>"
                              ])
        
        dlg.set_transient_for(self.dialog)
        dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dlg.show()

    def on_ipsecAddButton_clicked(self, *args):
        ipsecs = getIPsecList()
        ipsec = IPsec()

        canceled = self.ipsecDruid(ipsec)

        if canceled:
            return
        i = ipsecs.addIPsec()
        ipsecs[i].apply(ipsec)
        ipsecs[i].commit()
        ipsecs.commit()
        self.hydrateIPsec()

    def on_ipsecEditButton_clicked(self, *args):
        ipsecs = getIPsecList()
        clist  = self.xml.get_widget("ipsecList")

        if len(clist.selection) == 0:
            return

        ipsec = ipsecs[clist.selection[0]]

        canceled = self.ipsecDruid(ipsec)
        if canceled:
            return
        ipsecs.commit()

        self.hydrateIPsec()

    def ipsecDruid(self, ipsec):
        from editipsec import editIPsecDruid
        dialog = editIPsecDruid(ipsec)

        dl = dialog.druid

        dl.set_transient_for(self.dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)

        gtk.mainloop()            
        dl.destroy()

        return dialog.canceled

    def on_ipsecDeleteButton_clicked(self, *args):
        ipsecs = getIPsecList()

        clist  = self.xml.get_widget("ipsecList")

        if len(clist.selection) == 0:
            return

        del ipsecs[clist.selection[0]]
        ipsecs.commit()
        self.hydrateIPsec()

    def on_ipsecActivateButton_clicked(self, button):
        clist = self.xml.get_widget("ipsecList")

        if len(clist.selection) == 0:
            return
        
        ipsec = clist.get_row_data(clist.selection[0])
        
        if self.changed():
            button = generic_yesno_dialog(
                _("You have made some changes in your configuration.") + "\n"+\
                _("To activate the IPsec connection %s, "
                  "the changes have to be saved.") % (ipsec.IPsecId) \
                + "\n\n" + _("Do you want to continue?"),
                self.dialog)
                
            if button == RESPONSE_YES:
                if self.save() != 0:
                    return
            
            if button == RESPONSE_NO:
                return

        (status, txt) = ipsec.activate(dialog = self.dialog)

    def on_ipsecDeactivateButton_clicked(self, button):
        clist = self.xml.get_widget("ipsecList")
        if len(clist.selection) == 0:
            return

        ipsec = clist.get_row_data(clist.selection[0])
        
        if not ipsec:
            return

        (status, txt) = ipsec.deactivate(dialog = self.dialog)
        
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/10/08 15:18:17 $"
__version__ = "$Revision: 1.30 $"
