#! /usr/bin/env python
## redhat-network-control - A easy-to-use interface for configuring/activating
## Copyright (C) 2002 Red Hat, Inc.
## Copyright (C) 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2003 Harald Hoyer <harald@redhat.com>

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

if not '/usr/lib/rhs/python' in sys.path:
    sys.path.append("/usr/lib/rhs/python")

if not "/usr/share/redhat-config-network" in sys.path:
    sys.path.append("/usr/share/redhat-config-network")

if not "/usr/share/redhat-config-network/netconfpkg/" in sys.path:
    sys.path.append("/usr/share/redhat-config-network/netconfpkg")

PROGNAME='redhat-config-network'
import locale
from rhpl.translate import _, N_, textdomain_codeset
locale.setlocale(locale.LC_ALL, "")
textdomain_codeset(PROGNAME, locale.nl_langinfo(locale.CODESET))
import __builtin__
__builtin__.__dict__['_'] = _

import signal
import os
import os.path
import string
import gtk
import gtk.glade
from netconfpkg import *
from netconfpkg import Control
from netconfpkg.gui import *
from netconfpkg.gui.GUI_functions import GLADEPATH
from netconfpkg.gui.GUI_functions import DEFAULT_PROFILE_NAME
from rhpl.exception import handleException
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from rhpl.log import log

device = None

STATUS_COLUMN = 0
DEVICE_COLUMN = 1
NICKNAME_COLUMN = 2

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
#            'on_autoSelectProfileButton_clicked' : \
#            self.on_autoSelectProfileButton_clicked,
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
 
        self.tag = gtk.timeout_add(4000, self.update_dialog)
        # Let this dialog be in the taskbar like a normal window
        self.dialog.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        self.dialog.show()
        
    def on_Dialog_delete_event(self, *args):
        gtk.mainquit()

    def on_closeButton_clicked(self, button):
        gtk.mainquit()

    def on_infoButton_clicked(self, button):
        from version import PRG_VERSION
        from version import PRG_NAME
        dlg = gnome.ui.About(PRG_NAME,
                             PRG_VERSION,
                             _("Copyright (c) 2001-2003 Red Hat, Inc."),
                             _("This software is distributed under the GPL. "
                               "Please Report bugs to Red Hat's Bug Tracking "
                               "System: http://bugzilla.redhat.com/"),
                             ["Harald Hoyer <harald@redhat.com>",
                              "Than Ngo <than@redhat.com>",
                              "Philipp Knirsch <pknirsch@redhat.com>",
                              "Trond Eivind Glomsrød <teg@redhat.com>",
                              ])
        
        dlg.set_transient_for(self.dialog)
        dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dlg.show()
    
    def on_activateButton_clicked(self, button):
        device = self.clist_get_device()
        nickname = self.clist_get_nickname()
        for dev in getDeviceList():
            if dev.DeviceId == nickname:
                break
        else:
            return
        
        gtk.timeout_remove(self.tag)
        
        if device:
            # Network Device Control Dialog
            dlg = gtk.Dialog(_('Network device activating...'),
                             self.dialog,
                             gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
            label=gtk.Label(_('Activating network device %s, '\
                              'please wait...') %(nickname))
            dlg.vbox.add(label)
            dlg.set_border_width(10)
            dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            label.show()
            dlg.vbox.show()
            dlg.show_all()
            dlg.show_now()
            dlg.set_transient_for(self.dialog)
            dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            dlg.set_modal(TRUE)
            dlg.show_all()
            idle_func()
            (ret, msg) = dev.activate()
            dlg.destroy()
            
            self.update_dialog()

        self.tag = gtk.timeout_add(4000, self.update_dialog)
            
    def on_deactivateButton_clicked(self, button):
        device = self.clist_get_nickname()
        for dev in getDeviceList():
            if dev.DeviceId == device:
                break
        else:
            return
        if dev and device:
            (ret, msg) = dev.deactivate()
            self.update_dialog()

    def on_configureButton_clicked(self, button):
        device = self.clist_get_nickname()
        if not device:
            return
        
        for dev in getDeviceList():
            if dev.DeviceId == device:
                break
        else:
            return
        
        (ret, msg) = dev.configure()
        if ret:
            errorString = _('Cannot configure network device %s')\
                          % (device)
            generic_longinfo_dialog(errorString, msg, self.dialog);
            
        # update dialog #83640
        # Re-read the device list
        self.devicelist = self.getProfDeviceList(refresh=true)
        self.activedevicelist = NetworkDevice().get()
        # Update the gui
        self.hydrateProfiles(refresh = TRUE)
        self.hydrate(refresh = TRUE)
        self.oldprofile = None # forces a re-read of oldprofile
        self.update_dialog()
        
    def on_profileActivateButton_clicked(self, button):
        profile = self.get_active_profile().ProfileName

        generic_run_dialog(
            command = "/usr/bin/redhat-config-network-cmd",
            argv = [ "redhat-config-network-cmd", "-a", "-p", profile ],
            title = _("Switching Profiles"),
            label = _("Switching to profile %s") % profile,
            errlabel = _("Failed to switch to profile %s") % profile,
            dialog = self.dialog)
                           

        # Re-read the device list
        self.devicelist = self.getProfDeviceList(refresh=true)
        self.activedevicelist = NetworkDevice().get()
        # Update the gui
        self.hydrate()
        self.oldprofile = None # forces a re-read of oldprofile
        self.hydrateProfiles()
        self.update_dialog()

    def on_monitorButton_clicked(self, button):
        # TBD
        generic_error_dialog(_("To be rewritten!"))
        return

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
        dev = clist.get_pixtext(clist.selection[0], STATUS_COLUMN)[0]
        return dev

    def clist_get_device(self):
        clist = self.xml.get_widget('interfaceClist')
        if len(clist.selection) == 0:
            return
        dev = clist.get_pixtext(clist.selection[0], DEVICE_COLUMN)[0]
        return dev

    def clist_get_nickname(self):
        clist = self.xml.get_widget('interfaceClist')
        if len(clist.selection) == 0:
            return
        dev = clist.get_text(clist.selection[0], NICKNAME_COLUMN)
        return dev

    def hydrate(self, refresh = None):
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
            clist.set_pixtext(row, STATUS_COLUMN, status, 5, status_pixmap,
                              status_mask)
            clist.set_pixtext(row, DEVICE_COLUMN, devname, 5, device_pixmap,
                              device_mask)
            row = row + 1

    def hydrateProfiles(self, refresh = None):
        profilelist = getProfileList(refresh)
        
        self.no_profileentry_update = true # ???
        omenu = self.xml.get_widget('profileOption')

        if len(profilelist) == 1:
            self.xml.get_widget('profileFrame').hide()

        
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
            if prof.Active == true:
                name += _(" (active)")
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
        devlist = getDeviceList(refresh)
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
        NCProfileList.updateNetworkScripts()
        NCDeviceList.updateNetworkScripts()
    window = mainDialog()
    gtk.mainloop()

    sys.exit(0)
