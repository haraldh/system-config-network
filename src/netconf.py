#!/usr/bin/python2.2

## netconf - A network configuration tool
## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
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
from rhpl.log import log
# Just to be safe...
os.umask(0022)

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

if not "/usr/share/" + PROGNAME in sys.path:
    sys.path.append("/usr/share/" + PROGNAME)

# Workaround for buggy gtk/gnome commandline parsing python bindings.
cmdline = sys.argv[1:]
sys.argv = sys.argv[:1]

import locale
from rhpl.translate import _, N_, textdomain_codeset
locale.setlocale(locale.LC_ALL, "")
textdomain_codeset(PROGNAME, locale.nl_langinfo(locale.CODESET))
import __builtin__
__builtin__.__dict__['_'] = _

os.environ["PYgtk_FATAL_EXCEPTIONS"] = '1'

import os.path
import signal

try:
    from rhpl.exception import handleException
except RuntimeError, msg:
    print _("Error: %s, %s!") % (PROGNAME, msg)
    if os.path.isfile("/usr/sbin/redhat-config-network-tui"):        
        print _("Starting text version")
        os.execv("/usr/sbin/redhat-config-network-tui", sys.argv)
    sys.exit(10)


from version import PRG_VERSION
from version import PRG_NAME

sys.excepthook = lambda type, value, tb: handleException((type, value, tb),
                                                         PROGNAME, PRG_VERSION)

NETCONFDIR='/usr/share/redhat-config-network/'

try:
    import gtk
except RuntimeError:
    sys.stderr.write(_("ERROR: Unable to initialize graphical environment. ") + \
                     _("Most likely cause of failure is that the tool was not run using a graphical environment. ") + \
                     _("Please either start your graphical user interface or set your DISPLAY variable.\n"))
    sys.exit(0)

def get_pixpath(pixmap_file):
    fn = pixmap_file
    search_path = [ "",
                    "pixmaps/",
                    "../pixmaps/",
                    NETCONFDIR,
                    NETCONFDIR + "pixmaps/",
                    "/usr/share/pixmaps/" ]
    for sp in search_path:
        pixmap_file = sp + fn
        if os.path.exists(pixmap_file):
            break
    else:
        return None
    
    return pixmap_file

def splash_screen(gfx = None):
    if gfx:
        window = gtk.Window(gtk.WINDOW_POPUP)
        window.set_title(PRG_NAME)
        window.set_position (gtk.WIN_POS_CENTER)
        pixmap_wid = gtk.Image()
        pixfile = get_pixpath("redhat-config-network-splash.png")
        if not pixfile:
            return None
        pixmap_wid.set_from_file(pixfile)
        window.add(pixmap_wid)
        pixmap_wid.show_now()
    else:
        window = gtk.Window(gtk.WINDOW_POPUP)
        window.set_title(PRG_NAME)
        window.set_position (gtk.WIN_POS_CENTER)
        window.set_border_width(5)
        lbl = gtk.Label(_('Loading Network Configuration...'))
        window.add(lbl)
        lbl.show_now()

    window.show_all()
    window.show_now()
    
    while gtk.events_pending():
        gtk.main_iteration()

    return window

def Usage():
    print _("redhat-config-network - network configuration tool\n\nUsage: redhat-config-network -v --verbose")

def main():
    from netconfpkg import NC_functions
    log.set_loglevel(NC_functions.getVerboseLevel())
    splash_window = None

    try:
        #splash_window = splash_screen()
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

        
#         if splash_window:
#             splash_window.destroy()
#             del splash_window

        gtk.main()

    except SystemExit, code:
        #print "Exception %s: %s" % (str(SystemExit), str(code))
        sys.exit(code)
    except:
        if splash_window:
            splash_window.destroy()
            del splash_window
        handleException(sys.exc_info(), PROGNAME, PRG_VERSION)

if __name__ == '__main__':
    import getopt
    class BadUsage: pass
    splash_window = None
    from rhpl.log import log
    from netconfpkg import NC_functions
    NC_functions.setVerboseLevel(2)
    NC_functions.setDebugLevel(0)
    hotshot = 0
    chroot = None
    logfilename = "/var/log/redhat-config-network"
    
    try:
        opts, args = getopt.getopt(cmdline, "vhrd",
                                   [
                                    "verbose",
                                    "debug", 
                                    "help",
                                    "hotshot",
                                    "root"
                                    ])
        for opt, val in opts:
            if opt == '-v' or opt == '--verbose':
                NC_functions.setVerboseLevel(NC_functions.getVerboseLevel()+1)
                continue

            if opt == '-d' or opt == '--debug':
                NC_functions.setDebugLevel(NC_functions.getDebugLevel()+1)
                continue

            if opt == '--hotshot':
                hotshot += 1
                continue
            
            if opt == '-h' or opt == '--help':
                Usage()
                sys.exit(0)

            if opt == '-r' or opt == '--root':
                chroot = val
                continue

            raise BadUsage

    except (getopt.error, BadUsage):
        Usage()
        sys.exit(1)    

    if not NC_functions.getDebugLevel():
        import os
        
        def log_default_handler (string):
            import time
            log.logFile.write ("%s: %s\n" % (time.ctime(), string))

        log.handler = log_default_handler
        
	if os.path.isfile(logfilename):
            os.chmod(logfilename, 0600)
            
        fd = os.open(logfilename,
                        os.O_APPEND|os.O_WRONLY|os.O_CREAT,
                        0600)
        
        lfile = os.fdopen(fd, "a")        
        log.open(lfile)

    if chroot:
        prepareRoot(chroot)
        
    if hotshot:
        import tempfile
        from hotshot import Profile
        import hotshot.stats
        filename = tempfile.mktemp()
        prof = Profile(filename)
        try:
            prof = prof.runcall(main)
        except SystemExit:
            pass

        s = hotshot.stats.load(filename)
        s.strip_dirs().sort_stats('time').print_stats(20)
        s.strip_dirs().sort_stats('cumulative').print_stats(20)
        os.unlink(filename)               
    else:
        main()
        
    sys.exit(0)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/10/08 15:09:03 $"
__version__ = "$Revision: 1.195 $"
