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

PROGNAME='redhat-config-network'

import sys
import os
# Just to be safe...
os.umask(0022)

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

if not "/usr/share/" + PROGNAME in sys.path:
    sys.path.append("/usr/share/" + PROGNAME)

# Workaround for buggy gtk/gnome commandline parsing python bindings.
cmdline = sys.argv[1:]
sys.argv = sys.argv[:1]

import gettext

gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)

try:
    gettext.install(PROGNAME, "/usr/share/locale", 1)
except IOError:
    import __builtin__
    __builtin__.__dict__['_'] = unicode    

os.environ["PYgtk_FATAL_EXCEPTIONS"] = '1'

import os.path
import signal

try:
    from rhpl.exception import handleException
except RuntimeError, msg:
    print _("Error: %s, %s!") % (PROGNAME, msg)
    if os.path.isfile("/usr/sbin/redhat-config-network-tui"):        
        print _("Starting text version:")
        os.execv("/usr/sbin/redhat-config-network-tui", sys.argv)
    sys.exit(10)


from version import PRG_VERSION
from version import PRG_NAME

sys.excepthook = lambda type, value, tb: handleException((type, value, tb),
                                                         PROGNAME, PRG_VERSION)

NETCONFDIR='/usr/share/redhat-config-network/'

import gtk

def get_pixpath(pixmap_file):
    fn = pixmap_file
    if not os.path.exists(pixmap_file):
        pixmap_file = "pixmaps/" + fn
        if not os.path.exists(pixmap_file):
            pixmap_file = "../pixmaps/" + fn
            if not os.path.exists(pixmap_file):
                pixmap_file = NETCONFDIR + fn
                if not os.path.exists(pixmap_file):
                    pixmap_file = NETCONFDIR + "pixmaps/" + fn
                    if not os.path.exists(pixmap_file):
                        pixmap_file = "/usr/share/pixmaps/" + fn
                        if not os.path.exists(pixmap_file):
                            return None

    return pixmap_file

def splash_screen(gfx = None):
    if gfx:
        window = gtk.Window(gtk.WINDOW_POPUP)
        window.set_position (gtk.WIN_POS_CENTER)
        pixmap_wid = gtk.Image()
        pixfile = get_pixpath("redhat-config-network-splash.png")
        if not pixfile:
            return None
        pixmap_wid.set_from_file(pixfile)
        window.add(pixmap_wid)
        pixmap_wid.realize()
    else:
        window = gtk.Window()
        window.set_position (gtk.WIN_POS_CENTER)
        
        lbl = gtk.Label(_('Loading Network Configuration...'))
        window.add(lbl)
        
    window.show_all()
    while gtk.events_pending():
        gtk.main_iteration()

    return window

if __name__ == '__main__':
    splash_window = None
    try:
        splash_window = splash_screen()
        import gnome
        import gtk.glade
        import netconfpkg.gui.GUI_functions
        import netconfpkg
        netconfpkg.PRG_NAME = PRG_NAME
        from netconfpkg.gui.NewInterfaceDialog import NewInterfaceDialog
        from netconfpkg.gui.maindialog import mainDialog

        netconfpkg.gui.GUI_functions.PROGNAME = PROGNAME

        # make ctrl-C work
        signal.signal (signal.SIGINT, signal.SIG_DFL)

        progname = os.path.basename(sys.argv[0])

        showprofile = 1

        gnome.program_init(PROGNAME, PRG_VERSION)
        gtk.glade.bindtextdomain(PROGNAME, "/usr/share/locale")        

        if progname == 'redhat-config-network-druid' or \
               progname == 'internet-druid':
            interface = NewInterfaceDialog()
            gtk.mainloop()
            if interface.canceled:
                sys.exit(1)                

        window = mainDialog()
        
        if splash_window:
            splash_window.destroy()
            del splash_window
            
        gtk.main()

    except SystemExit, code:
        #print "Exception %s: %s" % (str(SystemExit), str(code))
        sys.exit(code)
    except:
        if splash_window:
            splash_window.destroy()
            del splash_window
        handleException(sys.exc_info(), PROGNAME, PRG_VERSION)

    sys.exit(0)
