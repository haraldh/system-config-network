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

PROGNAME='redhat-control-network'
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
_=gettext.gettext

import getopt
import signal
import os
import os.path
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

ACTIVE = _('Active')
INACTIVE = _('Inactive')

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
        self.lan_xpm, self.lan_mask = get_icon('pixmaps/ethernet.xpm', self.dialog)
        self.ppp_xpm, self.ppp_mask = get_icon('pixmaps/ppp.xpm', self.dialog)
        self.isdn_xpm, self.isdn_mask = get_icon('pixmaps/isdn.xpm', self.dialog)
        load_icon('pixmaps/control.xpm', self.dialog)
        self.xml.get_widget('pixmap').load_file('/usr/share/redhat-config-network/pixmaps/control.xpm')
        clist = self.xml.get_widget('interfaceClist')
        clist.column_titles_passive ()
        self.hydrate()
        
    def on_Dialog_delete_event(self, *args):
        gtk.mainquit()

    def on_closeButton_clicked(self, button):
        gtk.mainquit()

    def on_infoButton_clicked(self, button):
        dlg = gnome.ui.GnomeAbout(NAME, VERSION, COPYRIGHT, AUTORS, TEXT)
        dlg.run_and_close()

    def on_activateButton_clicked(self, button):
        device = self.clist_get_device()
        if device:
            child = Interface().activate(device)
            signal.signal(signal.SIGUSR1, self.handler)
            dlg = gtk.GtkWindow(gtk.WINDOW_DIALOG, _('Network device activating...'))
            dlg.set_border_width(10)
            vbox = gtk.GtkVBox(1)
            vbox.add(gtk.GtkLabel(_('Activating for Network device %s, please wait...') %(device)))
            dlg.add(vbox)
            dlg.set_position (gtk.WIN_POS_MOUSE)
            dlg.set_modal(TRUE)
            dlg.show_all()
            idle_func()
            time.sleep(1)
            os.waitpid(child, 0)
            dlg.destroy()
            if NetworkDevice().find(device):
                self.hydrate()
            else:
                self.errorDialog(device, ACTIVATE)
        
    def on_deactivateButton_clicked(self, button):
        device = self.clist_get_device()
        if device:
            ret = Interface().deactivate(device)
            if not ret:
                self.hydrate()
            else:
                self.errorDialog(device, DEACTIVATE)

    def on_configureButton_clicked(self, button):
        device = self.clist_get_device()
        if device:
            ret = Interface().configure(device)
            if not ret:
                self.hydrate()
            else:
                self.errorDialog(device, CONFIGURE)

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
            self.xml.get_widget('configureButton').set_sensitive(FALSE)
            self.xml.get_widget('monitorButton').set_sensitive(TRUE)
        else:
            self.xml.get_widget('activateButton').set_sensitive(TRUE)
            self.xml.get_widget('deactivateButton').set_sensitive(FALSE)
            self.xml.get_widget('configureButton').set_sensitive(TRUE)
            self.xml.get_widget('monitorButton').set_sensitive(FALSE)
        
        if activate_button: pass
        if deactivate_button: pass
        if configure_button: pass
        if monitor_button: pass

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
        devicelist = getDeviceList()
        activedevicelist = NetworkDevice().get()
        clist = self.xml.get_widget('interfaceClist')
        clist.clear()
        clist.set_row_height(20)
        status_pixmap = self.off_xpm
        status_mask = self.off_mask
        device_pixmap = self.lan_xpm
        device_mask = self.lan_mask
        status = INACTIVE
        row = 0
        
        for dev in devicelist:
            for i in activedevicelist:
                status = INACTIVE
                status_pixmap = self.off_xpm
                status_mask = self.off_mask
                if i == dev.Device:
                    status = ACTIVE
                    status_pixmap = self.on_xpm
                    status_mask = self.on_mask
                    break
            
            if dev.Device[:3] == 'ppp':
                device_pixmap = self.ppp_xpm
                device_mask = self.ppp_mask
            elif dev.Device[:3] == 'eth' or dev.Device[:5] == 'cipcb' or dev.Device[:2] == 'tr':
                device_pixmap = self.lan_xpm
                device_mask = self.lan_mask
            elif dev.Device[:4] == 'ippp' or dev.Device[:4] == 'isdn':
                device_pixmap = self.isdn_xpm
                device_mask = self.isdn_mask

            clist.append([status, dev.Device, dev.DeviceId])
            clist.set_pixtext(row, STATUS, status, 5, status_pixmap, status_mask)
            clist.set_pixtext(row, DEVICE, dev.Device, 5, device_pixmap, device_mask)
            row = row + 1
            
    def errorDialog(self, device, error_type):
        if error_type == ACTIVATE:
            errorString = _('cannot activate network device %s') %(device)
        elif error_type == DEACTIVATE:
            errorString = _('cannot deactivate network device %s') %(device)
        elif error_type == STATUS:
            errorString = _('cannot show status of network device %s') %(device)
        elif error_type == MONITOR:
            errorString = _('cannot monitor status of network device %s') %(device)

        dlg = gnome.ui.GnomeMessageBox(errorString, 'error', _('Close'))
        dlg.run_and_close()

    def handler(self):
        sys.exit(12)
        
def idle_func():
    while gtk.events_pending():
        gtk.mainiteration()
                    
# make ctrl-C work
if __name__ == '__main__':
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = mainDialog()
    gtk.mainloop()

    sys.exit(0)
