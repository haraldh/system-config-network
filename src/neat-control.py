#! /usr/bin/env python
## redhat-network-control - A easy-to-use interface for configuring/activating
## Copyright (C) 2002 Red Hat, Inc.
## Copyright (C) 2002 Than Ngo <than@redhat.com>

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
import gettext

if not '/usr/lib/rhs/python' in sys.path:
    sys.path.append("/usr/lib/rhs/python")

if not "/usr/share/redhat-config-network" in sys.path:
    sys.path.append("/usr/share/redhat-config-network")

if not "/usr/share/redhat-config-network/netconfpkg/" in sys.path:
    sys.path.append("/usr/share/redhat-config-network/netconfpkg")

PROGNAME='redhat-config-network'
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)

try:
    gettext.install(PROGNAME, "/usr/share/locale", 1)
except IOError:
    import __builtin__
    __builtin__.__dict__['_'] = unicode    

import getopt
import signal
import os
import os.path
import posix
import time
import string
import gtk
import gtk.glade
from netconfpkg import *
from netconfpkg import Control
from netconfpkg.gui import *
from netconfpkg.gui.GUI_functions import GLADEPATH
from netconfpkg.gui.GUI_functions import DEFAULT_PROFILE_NAME
from netconfpkg.gui.exception import handleException
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect

# Copyright
TEXT =  _("This software is distributed under the GPL. '\
'Please Report bugs to Red Hat's Bug Tracking System: '\
'http://bugzilla.redhat.com/")

device = None

# Some command strings
autoselect_profile_cmd = "/usr/bin/autostart_profile"
profile_up_cmd         = "/etc/sysconfig/network-scripts/profile_ctl up"
profile_down_cmd       = "/etc/sysconfig/network-scripts/profile_ctl down"
switch_profile_cmd     = "/usr/bin/redhat-config-network-cmd -p "

class mainDialog:
    def __init__(self):
        glade_file = 'neat-control.glade'

        if not os.path.isfile(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            'on_closeButton_clicked' : self.on_closeButton_clicked,
            'on_infoButton_clicked' : self.on_infoButton_clicked,
            'on_activateButton_clicked' : self.on_activateButton_clicked,
            'on_deactivateButton_clicked' : self.on_deactivateButton_clicked,
            'on_configureButton_clicked' : self.on_configureButton_clicked,
            'on_monitorButton_clicked' : self.on_monitorButton_clicked,
            'on_profileActivateButton_clicked' : \
            self.on_profileActivateButton_clicked,
            'on_autoSelectProfileButton_clicked' : \
            self.on_autoSelectProfileButton_clicked,
            'on_interfaceClist_select_row' : (\
            self.on_generic_clist_select_row,
            self.xml.get_widget('activateButton'),
            self.xml.get_widget('deactivateButton'),
            self.xml.get_widget('editButtonbutton'),
            self.xml.get_widget('monitorButton')),
            })

        self.dialog = self.xml.get_widget('mainWindow')
        self.dialog.connect('delete-event', self.on_Dialog_delete_event)
        self.dialog.connect('hide', gtk.mainquit)
        self.on_xpm, self.on_mask = get_icon('pixmaps/on.xpm', self.dialog)
        self.off_xpm, self.off_mask = get_icon('pixmaps/off.xpm', self.dialog)

        if not os.access('/usr/bin/rp3', os.X_OK):
            self.xml.get_widget('monitorButton').hide()

        load_icon('neat-control.xpm', self.dialog)
        self.xml.get_widget('pixmap').set_from_file(\
            '/usr/share/redhat-config-network/pixmaps/neat-control-logo.png')
        clist = self.xml.get_widget('interfaceClist')
        clist.column_titles_passive ()
        
        self.devicelist = self.getProfDeviceList()
        self.activedevicelist = NetworkDevice().get()
        self.hydrate()
        self.oldprofile = None
        self.xml.get_widget('profileActivateButton').set_sensitive(FALSE)
        self.hydrateProfiles()

        self.xml.get_widget('autoSelectProfileButton').hide()
 
        self.tag = timeout_add(4000, self.update_dialog)
        # Let this dialog be in the taskbar like a normal window
        self.dialog.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        self.dialog.show()
        
    def on_Dialog_delete_event(self, *args):
        gtk.mainquit()

    def on_closeButton_clicked(self, button):
        gtk.mainquit()

    def on_infoButton_clicked(self, button):
        print "TBD"
        #dlg = gnome.ui.GnomeAbout(NAME, VERSION, COPYRIGHT, AUTORS, TEXT)
        #dlg.run_and_close()
        pass
    
    def on_activateButton_clicked(self, button):
        device = self.clist_get_device()
        timeout_remove(self.tag)
        
        if device:
            intf = Interface()
            # Network Device Control Dialog
            dlg = gtk.Dialog(_('Network device activating...'),
                             self.dialog,
                             gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
            label=gtk.Label(_('Activating network device %s, '\
                              'please wait...') %(device))
            dlg.vbox.add(label)
            dlg.set_border_width(10)
            dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            label.show()
            dlg.vbox.show()
            dlg.show_now()
            dlg.set_transient_for(self.dialog)
            dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            dlg.set_modal(TRUE)
            dlg.show_all()
            #self.dialog.get_window().set_cursor(gtk.cursor_new(gtk.WATCH))
            #dlg.get_window().set_cursor(gtk.cursor_new(gtk.WATCH))
            idle_func()
            (ret, msg) = intf.activate(device)
            #self.dialog.get_window().set_cursor(gtk.cursor_new(gtk.LEFT_PTR))
            #dlg.get_window().set_cursor(gtk.cursor_new(gtk.LEFT_PTR))
            dlg.destroy()
            
            if NetworkDevice().find(device):
                self.update_dialog()
            else:
                devErrorDialog(device, ACTIVATE, self.dialog)

        self.tag = timeout_add(4000, self.update_dialog)
            
    def on_deactivateButton_clicked(self, button):
        device = self.clist_get_device()
        if device:
            (ret, msg) = Interface().deactivate(device)
            if not ret:
                self.update_dialog()
            else:
                devErrorDialog(device, DEACTIVATE, self.dialog)

    def on_configureButton_clicked(self, button):
        device = self.clist_get_device()
        if device:
            ret = Interface().configure(device)
            if ret:
                devErrorDialog(device, CONFIGURE, self.dialog)
                
    def activate_new_profile(self, profile):
        profilelist = getProfileList()        
        aprof = self.get_active_profile()
        print "Active Device List "
        print aprof.ActiveDevices
        for device in getDeviceList():
            if device.DeviceId in aprof.ActiveDevices:
                continue
            (ret, msg) = Interface().deactivate(device.DeviceId)
            if ret:
                devErrorDialog(device.DeviceId, DEACTIVATE, self.dialog)
                print msg

        print "Switching to profile %s" % profile
        profilelist.switchToProfile(profile)
        profilelist.save()
        aprof = profilelist.getActiveProfile()
        aprof = self.get_active_profile()
        
        print "Active Device List "
        print aprof.ActiveDevices
        for device in aprof.ActiveDevices:
            (ret, msg) = Interface().activate(device)
            if ret:
                devErrorDialog(device, ACTIVATE, self.dialog)
                print msg
        
        self.update_dialog()

        return 0

    def on_profileActivateButton_clicked(self, button):
        # Display dialog notification of action
        dlg = gtk.Dialog(_('Activating profile...'),
                         self.dialog,
                         gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
        label=gtk.Label(_('Activating the selected profile, please wait...'))
        dlg.vbox.add(label)
        dlg.set_border_width(10)
        dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        label.show()
        dlg.vbox.show()
        dlg.show_now()
        idle_func()
        
        # Disable the activate button
        self.xml.get_widget('profileActivateButton').set_sensitive(FALSE)
        # Get the profile to activate from the menu
        profilelist = getProfileList()
        profile = self.get_active_profile().ProfileName
        # Activate the selected profile
        status=self.activate_new_profile(profile)
        dlg.destroy()
        # Check results of the activation
        if status != 0:
            generic_error_dialog(_('Not all network interfaces in '\
                                   'selected profile \"%s\" could '\
                                   'be activated.') %(profile))
        # Re-read the device list
        self.devicelist = self.getProfDeviceList(refresh=true)
        self.activedevicelist = NetworkDevice().get()
        # Update the gui
        self.hydrate()
        self.oldprofile = None # forces a re-read of oldprofile
        self.hydrateProfiles()
        self.update_dialog()

    def on_autoSelectProfileButton_clicked(self, button):
        #import time
        import popen2
        import re
        # Make sure the user really wants to auto select ...
        yesno=generic_yesno_dialog('The system will now attempt to ' \
                                   'auto-detect and activate a valid network '\
                                   'profile.\n\nWarning: This process stops ' \
                                   'and restarts the network. Some currently'\
                                   ' active programs which are using the '\
                                   'network (servers in particular) may '\
                                   'exhibit problems afterwards.\n\nDo you '\
                                   'want to continue?')
        if yesno != gtk.RESPONSE_YES: return
        # Continue with auto select
        label=gtk.Label(_('Attempting to auto-detect and activate '\
                          'a valid profile, please wait...'))
        dlg = gtk.Dialog(_('Autoselecting profile...'),
                         self.dialog,
                         gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
        dlg.vbox.add(label)
        dlg.set_border_width(10)
        dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        label.show()
        dlg.vbox.show()
        dlg.show_now()
        idle_func()
        asp=popen2.Popen3(autoselect_profile_cmd,capturestderr=true)
        status=asp.wait()
        dlg.destroy()
        # Check status of the auto select script and respond accordingly
        if status != 0:		
            # Grab any error output
            errstr="Error:"
            for s in asp.childerr.readlines(): errstr=errstr + " " +s
            #errstr='Error: No available profile found. Network unavailable.'
            generic_error_dialog(_(errstr))
        else:
            # Grab the profile name from the output of the script
            profile = None
            for s in asp.fromchild.readlines(): 
                m=re.search('(?<=Using\ profile: ).*',s)
                if m != None:
                    profile=m.group()
                    self.set_profile_active(profile)
            # Re-read the device list
            self.devicelist = self.getProfDeviceList(refresh=true) 
            self.activedevicelist = NetworkDevice().get()
            # Update the gui
            self.oldprofile = None # forces a re-read of oldprofile
            self.hydrate()
            self.hydrateProfiles()
            self.update_dialog()

    def on_monitorButton_clicked(self, button):
        # TBD
        generic_error_dialog(_("To be rewritten!"))
        return
        device = self.clist_get_device()
        if device:
            Interface().monitor(device)

    def on_generic_clist_select_row(self, clist, row, column, event,
                                    activate_button = None,
                                    deactivate_button = None,
                                    configure_button = None,
                                    monitor_button = None):
        if len(clist.selection) == 0:
            return
        
        try:
            status = clist.get_pixtext(clist.selection[0], 0)[0]
        except ValueError:
            status = clist.get_text(clist.selection[0], 0)
            
        if status == ACTIVE:
            self.xml.get_widget('activateButton').set_sensitive(FALSE)
            self.xml.get_widget('deactivateButton').set_sensitive(TRUE)
            #self.xml.get_widget('configureButton').set_sensitive(FALSE)
            self.xml.get_widget('monitorButton').set_sensitive(TRUE)
        else:
            self.xml.get_widget('activateButton').set_sensitive(TRUE)
            self.xml.get_widget('deactivateButton').set_sensitive(FALSE)
            #self.xml.get_widget('configureButton').set_sensitive(TRUE)
            self.xml.get_widget('monitorButton').set_sensitive(FALSE)
        
    def clist_get_status(self):
        clist = self.xml.get_widget('interfaceClist')
        if len(clist.selection) == 0:
            return
        dev = clist.get_pixtext(clist.selection[0], STATUS)[0]
        return dev

    def clist_get_device(self):
        clist = self.xml.get_widget('interfaceClist')
        if len(clist.selection) == 0:
            return
        dev = clist.get_pixtext(clist.selection[0], DEVICE)[0]
        return dev

    def clist_get_nickname(self):
        clist = self.xml.get_widget('interfaceClist')
        if len(clist.selection) == 0:
            return
        dev = clist.get_text(clist.selection[0], NICKNAME)
        return dev

    def hydrate(self):
        plist = self.xml.get_widget('')
        clist = self.xml.get_widget('interfaceClist')
        clist.clear()
        clist.set_row_height(20)
        status_pixmap = self.off_xpm
        status_mask = self.off_mask
        status = INACTIVE
        row = 0
        
        for dev in self.devicelist:
            devname = dev.Device
            if dev.Alias and dev.Alias != "":
                devname = devname + ':' + str(dev.Alias)

            if devname in self.activedevicelist:
                status = ACTIVE
                status_pixmap = self.on_xpm
                status_mask = self.on_mask
            else:
                status = INACTIVE
                status_pixmap = self.off_xpm
                status_mask = self.off_mask

            device_pixmap, device_mask = GUI_functions.get_device_icon_mask(\
                dev.Type, self.dialog)
                
            clist.append([status, devname, dev.DeviceId])
            clist.set_pixtext(row, STATUS, status, 5, status_pixmap,
                              status_mask)
            clist.set_pixtext(row, DEVICE, devname, 5, device_pixmap,
                              device_mask)
            row = row + 1

    def hydrateProfiles(self):
        profilelist = getProfileList()
            
        self.no_profileentry_update = true # ???
        omenu = self.xml.get_widget('profileOption')
        omenu.remove_menu ()
        menu = gtk.Menu ()
        history = 0
        i = 0
        for prof in profilelist:
            name = prof.ProfileName
            # change the default profile to a more understandable name
            import netconf
            if name == "default":
                name = DEFAULT_PROFILE_NAME
            menu_item = gtk.MenuItem (name)
            menu_item.show ()
            menu_item.connect ("activate",
                               self.on_profileMenuItem_activated,
                               prof.ProfileName)
            menu.append (menu_item)
            if prof.ProfileName == self.get_active_profile().ProfileName:
                history = i
                if self.oldprofile == None:
                    self.oldprofile = prof.ProfileName  
            i = i+1
        if self.get_active_profile().ProfileName != self.oldprofile:
            self.xml.get_widget('interfaceClist').set_sensitive(FALSE)
        else:
            self.xml.get_widget('interfaceClist').set_sensitive(TRUE)
        menu.show ()
        omenu.set_menu (menu)
        omenu.set_history (history)
        menu.get_children()[history].activate ()
        self.no_profileentry_update = false # ??

    def get_active_profile(self):
        profilelist = getProfileList()
        return profilelist.getActiveProfile()
        
    def set_profile_active(self, profile):
        profilelist = getProfileList ()
        for prof in profilelist:
            if prof.ProfileName == profile:
                prof.Active = true
                #print "profile " + prof.ProfileName + " activated\n"
            else: prof.Active = false
            prof.commit()

    def getProfDeviceList(self, refresh=None):
        profilelist = getProfileList(refresh)
        prof=profilelist.getActiveProfile()
        devlist = getDeviceList()
        activedevlist = []
        for devid in prof.ActiveDevices:
            for dev in devlist:
                if dev.DeviceId != devid:
                    continue
                break
            else:
                continue
            activedevlist.append(dev)
        return activedevlist
        
    def on_profileMenuItem_activated(self, menu_item, profile):
        if not self.no_profileentry_update:
            self.set_profile_active(profile)            
            if self.oldprofile != self.get_active_profile().ProfileName:
                self.xml.get_widget('profileActivateButton' \
                                    ).set_sensitive(TRUE)
                self.xml.get_widget('interfaceClist').set_sensitive(FALSE)
                self.xml.get_widget('activateButton').set_sensitive(FALSE)
                self.xml.get_widget('deactivateButton').set_sensitive(FALSE)
            else:
                self.xml.get_widget('profileActivateButton' \
                                    ).set_sensitive(FALSE)
                self.xml.get_widget('interfaceClist').set_sensitive(TRUE)
                self.xml.get_widget('activateButton').set_sensitive(TRUE)
                self.xml.get_widget('deactivateButton').set_sensitive(TRUE)
    
    def update_dialog(self):
        activedevicelistold = self.activedevicelist
        self.activedevicelist = NetworkDevice().get()
        
        if activedevicelistold != self.activedevicelist:
            self.hydrate()
            return TRUE
            
        return TRUE


if __name__ == '__main__':
    # make ctrl-C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if os.getuid() == 0:        
        pl = NCProfileList.getProfileList()
        pl.updateNetworkScripts()
    window = mainDialog()
    gtk.mainloop()

    sys.exit(0)
