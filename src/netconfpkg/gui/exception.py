#
# exception.py - general exception formatting and saving
#
# Matt Wilson <msw@redhat.com>
# Erik Troan <ewt@redhat.com>
# Harald Hoyer <harald@redhat.com>
#
# Copyright 2001, 2002 Red Hat, Inc.
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
import gtk
from string import joinfields
from cPickle import Pickler
from netconfpkg.gui.GUI_functions import generic_error_dialog, get_icon, \
     WrappingLabel, addFrame
dumpHash = {}

from netconfpkg import PRG_VERSION
from netconfpkg import PROGNAME

from gtk import *

class ExceptionWindow:
    def __init__ (self, text):
        win = gtk.Dialog(_("Exception Occured"), None, gtk.DIALOG_MODAL)
        win.add_button(_("Debug"), 0)
        win.add_button(_("Save to file"), 1)
        win.add_button(gtk.STOCK_QUIT, 2)
        buffer = gtk.TextBuffer(None)
        buffer.set_text(text)
        textbox = gtk.TextView()
        textbox.set_buffer(buffer)
        textbox.set_property("editable", gtk.FALSE)
        textbox.set_property("cursor_visible", gtk.FALSE)
        sw = gtk.ScrolledWindow ()
        sw.add (textbox)
        sw.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox = gtk.HBox (gtk.FALSE)
        hbox.set_border_width(5)
        
        info = WrappingLabel(_("An unhandled exception has occured.  This "
                          "is most likely a bug.  Please save the crash "
                          "dump and file a detailed bug "
                          "report against redhat-config-network at "
                          '<A HREF="https://bugzilla.redhat.com/bugzilla/">https://bugzilla.redhat.com/bugzilla</a>'
                          ))
        info.set_use_markup(TRUE)
        info.set_size_request (400, -1)

        hbox.pack_start (sw, gtk.TRUE)
        win.vbox.pack_start (info, gtk.FALSE)
        win.vbox.pack_start (hbox, gtk.TRUE)
        win.vbox.set_border_width(5)
        win.set_size_request (500, 300)
        win.set_position (gtk.WIN_POS_CENTER)
        addFrame(win)
        win.show_all ()
        self.window = win
        self.rc = self.window.run ()
        self.window.destroy()

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
        import gnome.ui
        win = gtk.Dialog (_("Select a file:"))
        #win.connect ("clicked", self.quit)
        win.add_button (gtk.STOCK_OK, gtk.RESPONSE_OK)
        win.add_button (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        hbox = gtk.HBox (FALSE)

        info = gtk.Label(text)
        self.entry = gnome.ui.FileEntry("", "")
        self.entry.set_modal(TRUE)
        win.vbox.pack_start (info, FALSE)            
        win.vbox.pack_start (self.entry, TRUE)
        win.set_position (gtk.WIN_POS_CENTER)
        win.show_all ()
        self.window = win
        self.rc = self.window.run ()

    def quit (self, dialog, button):
        self.rc = button

    def getrc (self):
        return self.rc
    
    def get_filename(self):
        return self.entry.get_full_path(FALSE)
        
def handleException((type, value, tb)):
    list = traceback.format_exception (type, value, tb)
    tblast = traceback.extract_tb(tb, limit=None)
    if len(tblast):
        tblast = tblast[len(tblast)-1]
    extxt = traceback.format_exception_only(type, value)
    text = "Component: %s\n" % PROGNAME
    text = text + "Version: %s\n" % PRG_VERSION  
    text = text + "Summary: TB "
    for t in tblast:
        text = text + str(t) + ":"
    text = text + extxt[0]
    text = text + joinfields(list, "")

    while 1:
        rc = exceptionWindow (_("Exception Occurred"), text)
        
        if rc == 1 and tb:
            print text
            import pdb
            pdb.post_mortem (tb)
            os.kill(os.getpid(), signal.SIGKILL)
        elif not rc:
            sys.exit(10)
        else:
            fs = FileSelection(_("Please specify a file to save the dump"))
            rc = fs.getrc()
            if rc == gtk.RESPONSE_OK:
                file = fs.get_filename()
                print file
                fs.window.destroy()
                
                if not file or file=="":
                    file = "/tmp/dump"

                try:
                    out = open(file, "w")
                    dumpException (out, text, tb)
                    out.close()

                except IOError:
                    generic_error_dialog(_("Failed to write to file %s.") \
                                         % (file), None)
                else:
                    generic_error_dialog(
                        _("The application's state has been successfully\n"
                          "written to the file '%s'.") % (file), None,
                        dialog_type = "info")
                    sys.exit(10)
            
            else:
                continue
        
    sys.exit(10)

