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
import string
import signal

try:
    from netconfpkg.gui.exception import handleException
except RuntimeError, msg:
    print _("Error: %s, %s!") % (PROGNAME, msg)
    if os.path.isfile("/usr/sbin/redhat-config-network-tui"):        
        print _("Starting text version:")
        os.execv("/usr/sbin/redhat-config-network-tui", sys.argv)
    sys.exit(10)


sys.excepthook = lambda type, value, tb: handleException((type, value, tb))

if __name__ == '__main__':
    try:
        import gnome
        import gtk.glade
        import netconfpkg.gui.GUI_functions
        from netconfpkg.gui.NewInterfaceDialog import NewInterfaceDialog
        from netconfpkg.gui.maindialog import mainDialog

        netconfpkg.gui.GUI_functions.PROGNAME = PROGNAME

        # make ctrl-C work
        signal.signal (signal.SIGINT, signal.SIG_DFL)

        progname = os.path.basename(sys.argv[0])

        showprofile = 1

        gnome.program_init(PROGNAME, netconfpkg.PRG_VERSION)
        gtk.glade.bindtextdomain(PROGNAME, "/usr/share/locale")
        

        if progname == 'redhat-config-network-druid' or \
               progname == 'internet-druid':
            interface = NewInterfaceDialog()
            gtk.mainloop()
            if interface.canceled:
                sys.exit(1)                

        window = mainDialog()
        gtk.main()

    except SystemExit, code:
        #print "Exception %s: %s" % (str(SystemExit), str(code))
        sys.exit(code)
    except:
        handleException(sys.exc_info())

    sys.exit(0)
