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
_=gettext.gettext

import getopt
import signal
import os
import os.path
import posix
import time
import string
import GDK
import gtk
import libglade
import gnome
import gnome.ui
import gnome.help
from netconfpkg import *
from netconfpkg import Control
from netconfpkg.gui import *
from netconfpkg.gui.GUI_functions import GLADEPATH
from netconfpkg.gui.exception import handleException

TEXT =  _("This software is distributed under the GPL. Please Report bugs to Red Hat's Bug Tracking System: http://bugzilla.redhat.com/")

device = None

class mainDialog:
    def __init__(self):
        glade_file = 'neat-control.glade'

        if not os.path.isfile(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain=PROGNAME)

        self.xml.signal_autoconnect(
            {
            'on_closeButton_clicked' : self.on_closeButton_clicked,
            'on_infoButton_clicked' : self.on_infoButton_clicked,
            'on_activateButton_clicked' : self.on_activateButton_clicked,
            'on_deactivateButton_clicked' : self.on_deactivateButton_clicked,
            'on_configureButton_clicked' : self.on_configureButton_clicked,
            'on_monitorButton_clicked' : self.on_monitorButton_clicked,
            'on_interfaceClist_select_row' : (self.on_generic_clist_select_row,
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
        
        load_icon('neat-control.xpm', self.dialog)
        self.xml.get_widget('pixmap').load_file('/usr/share/redhat-config-network/pixmaps/neat-control-logo.png')
        clist = self.xml.get_widget('interfaceClist')
        clist.column_titles_passive ()
        
        self.devicelist = getDeviceList()
        self.activedevicelist = NetworkDevice().get()
        self.hydrate()
        
        self.tag = timeout_add(4000, self.update_dialog)
        
    def on_Dialog_delete_event(self, *args):
        gtk.mainquit()

    def on_closeButton_clicked(self, button):
        gtk.mainquit()

    def on_infoButton_clicked(self, button):
        dlg = gnome.ui.GnomeAbout(NAME, VERSION, COPYRIGHT, AUTORS, TEXT)
        dlg.run_and_close()

    def on_activateButton_clicked(self, button):
        device = self.clist_get_device()
        timeout_remove(self.tag)
        
        if device:
            intf = Interface()
            child = intf.activate(device)
            dlg = gtk.GtkWindow(gtk.WINDOW_DIALOG, _('Network device activating...'))
            dlg.set_border_width(10)
            vbox = gtk.GtkVBox(1)
            vbox.add(gtk.GtkLabel(_('Activating for Network device %s, please wait...') %(device)))
            vbox.show()
            dlg.add(vbox)
            dlg.set_position (gtk.WIN_POS_MOUSE)
            dlg.set_modal(TRUE)
            dlg.show_all()
            self.dialog.get_window().set_cursor(gtk.cursor_new(GDK.WATCH))
            dlg.get_window().set_cursor(gtk.cursor_new(GDK.WATCH))
            idle_func()
            os.waitpid(child, 0)
            self.dialog.get_window().set_cursor(gtk.cursor_new(GDK.LEFT_PTR))
            dlg.get_window().set_cursor(gtk.cursor_new(GDK.LEFT_PTR))
            dlg.destroy()
            
            if NetworkDevice().find(device):
                self.update_dialog()
            else:
                devErrorDialog(device, ACTIVATE, self.dialog)

        self.tag = timeout_add(4000, self.update_dialog)
            
    def on_deactivateButton_clicked(self, button):
        device = self.clist_get_device()
        if device:
            ret = Interface().deactivate(device)
            if not ret:
                self.update_dialog()
            else:
                devErrorDialog(device, DEACTIVATE, self.dialog)

    def on_configureButton_clicked(self, button):
        device = self.clist_get_device()
        if device:
            ret = Interface().configure(device)
            if not ret:
                self.hydrate()
            else:
                devErrorDialog(device, CONFIGURE, self.dialog)

    def on_monitorButton_clicked(self, button):
        device = self.clist_get_device()
        if device:
            Interface().monitor(device)

    def on_generic_clist_select_row(self, clist, row, column, event,
                                    activate_button = None, deactivate_button = None,
                                    configure_button = None, monitor_button = None):
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

            device_pixmap, device_mask = GUI_functions.get_device_icon_mask(dev.Type, self.dialog)
                
            clist.append([status, devname, dev.DeviceId])
            clist.set_pixtext(row, STATUS, status, 5, status_pixmap, status_mask)
            clist.set_pixtext(row, DEVICE, devname, 5, device_pixmap, device_mask)
            row = row + 1
            
    def update_dialog(self):
        activedevicelistold = self.activedevicelist
        self.activedevicelist = NetworkDevice().get()
        
        if activedevicelistold != self.activedevicelist:
            self.hydrate()
            return TRUE
            
        return TRUE


# make ctrl-C work
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if os.getuid() == 0: updateNetworkScripts()
    window = mainDialog()
    gtk.mainloop()

    sys.exit(0)
