#
# exception.py - general exception formatting and saving
#
# Matt Wilson <msw@redhat.com>
# Erik Troan <ewt@redhat.com>
# Harald Hoyer <harald@redhat.com>
#
# Copyright 2001 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import os, sys
import signal
import traceback
import types
import rpm
from string import joinfields
from cPickle import Pickler
from netconfpkg.NC_functions import _
from netconfpkg.gui.NC_functions import generic_error_dialog, get_icon
dumpHash = {}

import gnome
from gnome.ui import *
from gtk import *

class ExceptionWindow:
    def __init__ (self, text):
        win = GnomeDialog ("Exception Occured")
        win.connect ("clicked", self.quit)
        win.append_button ("Debug")
        win.append_button ("Save to file")
        win.append_button_with_pixmap ("OK", STOCK_BUTTON_OK)
        textbox = GtkText()
        textbox.insert_defaults (_("Please visit http://bugzilla.redhat.com/bugzilla/ !\nFile a bug against component redhat-config-network. Thank you!\n\n%s") % text)
        sw = GtkScrolledWindow ()
        sw.add (textbox)
        sw.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)

        hbox = GtkHBox (FALSE)
        pix, mask = get_icon('gnome-warning.png', win)
        if pix:
            hbox.pack_start (GnomePixmap (pix), FALSE)

        info = GtkLabel(_("An unhandled exception has occured.  This "
                          "is most likely a bug.  Please copy the "
                          "full text of this exception or save the crash "
                          "dump to a file then file a detailed bug "
                          "report against redhat-config-network at "
                          "http://bugzilla.redhat.com/bugzilla/"))
        info.set_line_wrap (TRUE)
        info.set_usize (400, -1)

        hbox.pack_start (sw, TRUE)
        win.vbox.pack_start (info, FALSE)            
        win.vbox.pack_start (hbox, TRUE)
        win.set_usize (500, 300)
        win.set_position (WIN_POS_MOUSE)
        win.show_all ()
        self.window = win
        self.rc = self.window.run ()
        
    def quit (self, dialog, button):
        self.rc = button

    def getrc (self):
        # I did it this way for future expantion
        # 0 is debug
        if self.rc == 0:
            return 1
        # 1 is save
        if self.rc == 1:
            return 2
        # 2 is OK
        elif self.rc == 2:
            return 0


# XXX do length limits on obj dumps.
def dumpClass(instance, fd, level=0):
    # protect from loops
    if not dumpHash.has_key(instance):
        dumpHash[instance] = None
    else:
        fd.write("Already dumped\n")
        return
    if (instance.__class__.__dict__.has_key("__str__") or
        instance.__class__.__dict__.has_key("__repr__")):
        fd.write("%s\n" % (instance,))
        return
    fd.write("%s instance, containing members:\n" %
             (instance.__class__.__name__))
    pad = ' ' * ((level) * 2)
    for key, value in instance.__dict__.items():
        if type(value) == types.ListType:
            fd.write("%s%s: [" % (pad, key))
            first = 1
            for item in value:
                if not first:
                    fd.write(", ")
                else:
                    first = 0
                if type(item) == types.InstanceType:
                    dumpClass(item, fd, level + 1)
                else:
                    fd.write("%s" % (item,))
            fd.write("]\n")
        elif type(value) == types.DictType:
            fd.write("%s%s: {" % (pad, key))
            first = 1
            for k, v in value.items():
                if not first:
                    fd.write(", ")
                else:
                    first = 0
                if type(k) == types.StringType:
                    fd.write("'%s': " % (k,))
                else:
                    fd.write("%s: " % (k,))
                if type(v) == types.InstanceType:
                    dumpClass(v, fd, level + 1)
                else:
                    fd.write("%s" % (v,))
            fd.write("}\n")
        elif type(value) == types.InstanceType:
            fd.write("%s%s: " % (pad, key))
            dumpClass(value, fd, level + 1)
        else:
            fd.write("%s%s: %s\n" % (pad, key, value))

def dumpException(out, text, tb):
    p = Pickler(out)

    out.write(text)

    trace = tb
    while trace.tb_next:
        trace = trace.tb_next
    frame = trace.tb_frame
    out.write ("\nLocal variables in innermost frame:\n")
    try:
        for (key, value) in frame.f_locals.items():
            out.write ("%s: %s\n" % (key, value))
    except:
        pass


def exceptionWindow(title, text):
    #print text
    win = ExceptionWindow (text)
    return win.getrc ()

class FileSelection:
    def __init__(self, text):
        win = GnomeDialog (_("Select a file:"))
        win.connect ("clicked", self.quit)
        win.append_button_with_pixmap ("OK", STOCK_BUTTON_OK)
        win.append_button_with_pixmap ("CANCEL", STOCK_BUTTON_CANCEL)
        hbox = GtkHBox (FALSE)

        info = GtkLabel(text)
        self.entry = GnomeFileEntry()
        win.vbox.pack_start (info, FALSE)            
        win.vbox.pack_start (self.entry, TRUE)
        win.set_position (WIN_POS_MOUSE)
        win.show_all ()
        self.window = win
        self.rc = self.window.run ()

    def quit (self, dialog, button):
        self.rc = button

    def getrc (self):
        return self.rc
    
    def get_filename(self):
        return self.entry.gtk_entry().get_text()
        
def handleException((type, value, tb)):
    list = traceback.format_exception (type, value, tb)
    text = joinfields (list, "")
    rc = exceptionWindow (_("Exception Occurred"), text)
    if rc == 1 and tb:
        print text
        import pdb
        pdb.post_mortem (tb)
        os.kill(os.getpid(), signal.SIGKILL)
    elif not rc:
        sys.exit(10)

    while 1:
        fs = FileSelection(_("Please specify a file to save the dumb"))
        rc = fs.getrc()
        if rc == 0:
            file = fs.get_filename()
            if not file or file=="":
                file = "/tmp/dump"

            try:
                out = open(file, "w")
                dumpException (out, text, tb)
                out.close()

            except IOError:
                generic_error_dialog(_("Failed to write to file %s.") % (file),
                                     None)
            else:
                generic_error_dialog(
                    _("The application's state has been successfully\n"
                      "written to the file '%s'.") % (file), None,
                    dialog_type = "info")
                sys.exit(10)
            
        else:
            break
        
    sys.exit(10)

