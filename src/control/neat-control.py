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

PROGNAME = 'redhat-network-control'
MAINDIR = '/usr/share/' + PROGNAME
NEATDIR = '/usr/share/redhat-config-network'

if not '/usr/lib/rhs/python' in sys.path:
    sys.path.append("/usr/lib/rhs/python")

if not MAINDIR in sys.path:
    sys.path.append(MAINDIR)

if not NEATDIR in sys.path:
    sys.path.append(NEATDIR)

# Workaround for buggy gtk/gnome commandline parsing python bindings.
cmdline = sys.argv[1:]
sys.argv = sys.argv[:1]

import getopt
import signal
import os
import os.path
import string
import gettext
import GDK
import gtk
import libglade
import gnome
import gnome.ui
import gnome.help
from functions import *
from netconfpkg import *

##
## I18N
##
gettext.bindtextdomain(PROGNAME, '/usr/share/locale')
gettext.textdomain(PROGNAME)
_ = gettext.gettext

TEXT =  _("This software is distributed under the GPL. Please Report bugs to Red Hat's Bug Tracking System: http://bugzilla.redhat.com/")

ACTIVE = _('Active')
INACTIVE = _('Inactive')

class mainDialog:
    def __init__(self):
        glade_file = 'maindialog.glade'

        if not os.path.isfile(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = MAINDIR + glade_file

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
        load_icon('pixmaps/control.xpm', self.dialog)
        self.xml.get_widget('pixmap').load_file('pixmaps/control.xpm')
        self.hydrate()
        
    def on_Dialog_delete_event(self, *args):
        gtk.mainquit()

    def on_closeButton_clicked(self, button):
        gtk.mainquit()

    def on_infoButton_clicked(self, button):
        dlg = gnome.ui.GnomeAbout(PROGNAME, VERSION, COPYRIGHT, AUTORS, TEXT)
        dlg.run_and_close()
        
    def on_activateButton_clicked(self, button):
        print 'activate button clicked'

    def on_deactivateButton_clicked(self, button):
        print 'deactivate button clicked'

    def on_configureButton_clicked(self, button):
        print 'configure button clicked'

    def on_monitorButton_clicked(self, button):
        print 'monitor button clicked'

    def on_generic_clist_select_row(self, clist, row, column, event,
                                    activate_button = None, deactivate_button = None,
                                    configure_button = None, monitor_button = None):
        if clist.get_text(clist.selection[0], 0) == ACTIVE:
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

    def hydrate(self):
        devicelist = getDeviceList()
        activedevicelist = ProcNetDevice().load()
        clist = self.xml.get_widget('interfaceClist')
        clist.clear()
        on_xpm, mask = get_icon ('pixmaps/on.xpm', self.dialog)
        off_xpm, mask = get_icon ('pixmaps/off.xpm', self.dialog)
        
        for dev in devicelist:
            for i in activedevicelist:
                status = INACTIVE
                if i == dev.Device:
                    status = ACTIVE
                    break
            clist.append([status, dev.Device, dev.DeviceId])



def get_icon(pixmap_file, dialog):
    fn = pixmap_file
    if not os.path.exists(pixmap_file):
        pixmap_file = 'pixmaps/' + fn
    if not os.path.exists(pixmap_file):
        pixmap_file = '../pixmaps/' + fn
    if not os.path.exists(pixmap_file):
        pixmap_file = NETCONFDIR + fn
    if not os.path.exists(pixmap_file):
         pixmap_file = NETCONFDIR + 'pixmaps/' + fn
    if not os.path.exists(pixmap_file):
        return None, None

    pix, mask = gtk.create_pixmap_from_xpm(dialog, None, pixmap_file)
    return pix, mask

def load_icon(pixmap_file, dialog):
    if not dialog: return

    pix, mask = get_icon(pixmap_file, dialog)
    if not pix: return

    gtk.GtkPixmap(pix, mask)
    if dialog: dialog.set_icon(pix, mask)


# make ctrl-C work
if __name__ == '__main__':
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = mainDialog()
    gtk.mainloop()

    sys.exit(0)
