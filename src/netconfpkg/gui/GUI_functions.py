## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>

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
import os
import gtk
import gtk.glade

from gtk import TRUE
from gtk import FALSE

from netconfpkg.NC_functions import *
from netconfpkg import NC_functions

gtk.glade.bindtextdomain(PROGNAME, "/usr/share/locale")

GLADEPATH='netconfpkg/gui/'

DEVPIXMAPS = {}

NC_functions.RESPONSE_NONE = gtk.RESPONSE_NONE
NC_functions.RESPONSE_REJECT = gtk.RESPONSE_REJECT
NC_functions.RESPONSE_ACCEPT = gtk.RESPONSE_ACCEPT
NC_functions.RESPONSE_DELETE_EVENT = gtk.RESPONSE_DELETE_EVENT
NC_functions.RESPONSE_OK = gtk.RESPONSE_OK
NC_functions.RESPONSE_CANCEL = gtk.RESPONSE_CANCEL
NC_functions.RESPONSE_CLOSE = gtk.RESPONSE_CLOSE
NC_functions.RESPONSE_YES = gtk.RESPONSE_YES
NC_functions.RESPONSE_NO = gtk.RESPONSE_NO
NC_functions.RESPONSE_APPLY = gtk.RESPONSE_APPLY
NC_functions.RESPONSE_HELP = gtk.RESPONSE_HELP

def get_device_icon_mask(devtype, dialog):
    if not DEVPIXMAPS.has_key(ETHERNET):
        DEVPIXMAPS[ETHERNET] = get_icon('pixmaps/ethernet.xpm', dialog)
        DEVPIXMAPS[MODEM] = get_icon('pixmaps/ppp.xpm', dialog)
        DEVPIXMAPS[ISDN] = get_icon('pixmaps/isdn.xpm', dialog)
        DEVPIXMAPS[WIRELESS] = get_icon('pixmaps/irda-16.xpm', dialog)
        DEVPIXMAPS[DSL] = get_icon('pixmaps/dsl.xpm', dialog)
        DEVPIXMAPS[TOKENRING] = DEVPIXMAPS[ETHERNET]
        DEVPIXMAPS[CIPE] = DEVPIXMAPS[ETHERNET]

    if not DEVPIXMAPS.has_key(devtype):
        return DEVPIXMAPS[ETHERNET]
    else:
        return DEVPIXMAPS[devtype]

def get_history (omenu):
    menu = omenu.get_menu ().get_active ()
    index = 0
    for menu_item in omenu.get_menu ().get_children():
        if menu_item == menu:
            break
        index = index + 1
    return index

def idle_func():
    while gtk.events_pending():
        gtk.mainiteration()

def get_pixbuf(pixmap_file):
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
                            return None, None

    pixbuf = gtk.gdk.pixbuf_new_from_file(pixmap_file)

    return pixbuf

def get_icon(pixmap_file, dialog = None):
    pixbuf = get_pixbuf(pixmap_file)
    
    pix, mask = pixbuf.render_pixmap_and_mask()
    
    return pix, mask

def load_icon(pixmap_file, dialog):
    if not dialog: return
 
    pixbuf = get_pixbuf(pixmap_file)
    if not pixbuf: return
     
    if dialog: dialog.set_icon(pixbuf)

def gui_error_dialog (message, parent_dialog,
                      message_type=gtk.MESSAGE_ERROR,
                      widget=None, page=0, broken_widget=None):
    
    dialog = gtk.MessageDialog(parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type, gtk.BUTTONS_OK,
                               message)
    
    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)

    if parent_dialog:
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_transient_for(parent_dialog)
    else:
        dialog.set_position (gtk.WIN_POS_CENTER)

    ret = dialog.run ()
    dialog.destroy()
    return ret

def gui_info_dialog (message, parent_dialog,
                      message_type=gtk.MESSAGE_INFO,
                      widget=None, page=0, broken_widget=None):
    
    dialog = gtk.MessageDialog(parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type, gtk.BUTTONS_OK,
                               message)
    
    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)

    if parent_dialog:
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_transient_for(parent_dialog)
    else:
        dialog.set_position (gtk.WIN_POS_CENTER)

    ret = dialog.run ()
    dialog.destroy()
    return ret

def gui_longinfo_dialog (message, long_message, parent_dialog,
                         message_type=gtk.MESSAGE_INFO,
                         widget=None, page=0, broken_widget=None):
    
    dialog = gtk.MessageDialog(parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type, gtk.BUTTONS_OK,
                               str(message))
    
    vbox=dialog.get_children()[0]
    buffer = gtk.TextBuffer(None)
    buffer.set_text(str(long_message))
    textbox = gtk.TextView()
    textbox.set_buffer(buffer)
    textbox.set_property("editable", gtk.FALSE)
    textbox.set_property("cursor_visible", gtk.FALSE)
    sw = gtk.ScrolledWindow ()
    sw.add (textbox)
    sw.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    hbox = gtk.HBox (gtk.FALSE)
    hbox.set_border_width(5)
    hbox.pack_start (sw, gtk.TRUE)
    vbox.pack_start (hbox, gtk.TRUE)

    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)

    if parent_dialog:
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_transient_for(parent_dialog)
    else:
        dialog.set_position (gtk.WIN_POS_CENTER)

    dialog.show_all()
    ret = dialog.run ()
    dialog.destroy()
    return ret

def gui_error_dialog (message, parent_dialog,
                      message_type=gtk.MESSAGE_ERROR,
                      widget=None, page=0, broken_widget=None):
    
    dialog = gtk.MessageDialog(parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type, gtk.BUTTONS_OK,
                               message)
    
    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)
        
    if parent_dialog:
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_transient_for(parent_dialog)
    else:
        dialog.set_position (gtk.WIN_POS_CENTER)
        
    ret = dialog.run ()
    dialog.destroy()
    return ret


def gui_yesnocancel_dialog (message, parent_dialog,
                            message_type=gtk.MESSAGE_QUESTION,
                            widget=None, page=0, broken_widget=None):
    dialog = gtk.MessageDialog(parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type,
                               gtk.BUTTONS_YES_NO,
                               message)
    dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)

    dialog.set_default_response(gtk.RESPONSE_REJECT)

    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)

    if parent_dialog:
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_transient_for(parent_dialog)
    else:
        dialog.set_position (gtk.WIN_POS_CENTER)

    ret = dialog.run ()
    dialog.destroy()

    if ret == gtk.RESPONSE_YES:
        return RESPONSE_YES
    elif ret == gtk.RESPONSE_NO:
        return RESPONSE_NO

    return RESPONSE_CANCEL

def gui_yesno_dialog (message, parent_dialog,
                      message_type=gtk.MESSAGE_QUESTION,
                      widget=None, page=0, broken_widget=None):

    dialog = gtk.MessageDialog(parent_dialog,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type,
                               gtk.BUTTONS_YES_NO,
                               message)
    if widget != None:
        if isinstance (widget, gtk.CList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.Notebook):
            widget.set_current_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.Entry):
            broken_widget.select_region (0, -1)

    if parent_dialog:
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_transient_for(parent_dialog)
    else:
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)

    ret = dialog.run ()
    dialog.destroy()

    if ret == gtk.RESPONSE_YES:
        return RESPONSE_YES

    return RESPONSE_NO

set_generic_info_dialog_func(gui_info_dialog)
set_generic_longinfo_dialog_func(gui_longinfo_dialog)
set_generic_error_dialog_func(gui_error_dialog)
set_generic_yesnocancel_dialog_func(gui_yesnocancel_dialog)
set_generic_yesno_dialog_func(gui_yesno_dialog)

def addFrame(dialog):
    contents = dialog.get_children()[0]
    dialog.remove(contents)
    frame = gtk.Frame()
    frame.set_shadow_type(gtk.SHADOW_OUT)
    frame.add(contents)
    dialog.add(frame)

def xml_signal_autoconnect (xml, map):
    for (signal, func) in map.items():
        if isinstance(func, tuple):
            xml.signal_connect(signal, *func)
        else:                
            xml.signal_connect(signal, func)


def gui_run(command, argv, searchPath = 0,
              root = '/', stdin = 0,
              catchfd = 1, closefd = -1):
    import gtk
    import os
    import select
    import string
    
    if not os.access (root + command, os.X_OK):
	raise RuntimeError, command + " can not be run"

    (read, write) = os.pipe()

    childpid = os.fork()
    if (not childpid):
        if (root and root != '/'): os.chroot (root)
        if isinstance(catchfd, tuple):
            for fd in catchfd:
                os.dup2(write, fd)
        else:
            os.dup2(write, catchfd)
	os.close(write)
	os.close(read)

	if closefd != -1:
	    os.close(closefd)

	if stdin:
	    os.dup2(stdin, 0)
	    os.close(stdin)

	if (searchPath):
	    os.execvp(command, argv)
	else:
	    os.execv(command, argv)

	sys.exit(1)
    try:
        os.close(write)

        rc = ""
        s = "1"
        while (s):
            try:
                (fdin, fdout, fderr) = select.select([read], [], [], 0.1)
            except:
                fdin = []
                pass

            while gtk.events_pending():
                gtk.mainiteration()
            
            if len(fdin):
                s = os.read(read, 100)
                rc = rc + s

    except Exception, e:
        os.kill(childpid, 15)
        raise e
        
    os.close(read)
    
    try:
        (pid, status) = os.waitpid(childpid, 0)
    except OSError, (errno, msg):
        #print __name__, "waitpid:", msg
        pass
    
    if os.WIFEXITED(status) and (os.WEXITSTATUS(status) == 0):
        status = os.WEXITSTATUS(status)
    else:
        status = -1

    return (status, rc)

__cancelPressed = None
__dialogClosed = None

def gui_run_dialog(command, argv, searchPath = 0,
              root = '/', stdin = 0,
              catchfd = 1, closefd = -1, title = None,
              label = None, errlabel = None, dialog = None):
    import gtk
    import os
    import select
    import string
    global __cancelPressed
    global __dialogClosed
    class CancelException: pass
    
    __cancelPressed = 0
    __dialogClosed = 0
    xml = __getXmlFile()
    dlg = xml.get_widget ("Dialog")
    lbl = xml.get_widget ("label")
    swindow = xml.get_widget ("swindow")
    xml.get_widget("statusImage").set_from_stock("gtk-dialog-info", 6)
    xml.signal_autoconnect({ "on_cancelbutton_clicked" :
                             __on_cancelbutton_clicked,
                             "on_Dialog_close" :
                             __on_Dialog_close,
                             "on_okbutton_clicked" :
                             __on_okbutton_clicked,
                             })
    
    dlg.connect("delete-event", __on_Dialog_close)
    dlg.connect("hide", __on_Dialog_close)
    if title:
        dlg.set_title(title)
    okbutton = xml.get_widget ("okbutton")
    okbutton.set_sensitive (gtk.FALSE)
    cancelbutton = xml.get_widget ("cancelbutton")
    cancelbutton.set_sensitive (gtk.TRUE)
    lbl.set_text(label)
    lbl.set_line_wrap(gtk.TRUE)
    textview = xml.get_widget ("textview")
    textview.set_property("editable", gtk.FALSE)
    textview.set_wrap_mode(gtk.WRAP_WORD)
    buffer = gtk.TextBuffer(None)
    mark = buffer.create_mark("end", buffer.get_start_iter(),
                              left_gravity=gtk.FALSE)
    textview.set_buffer(buffer)
    if dialog:
        dlg.set_transient_for(dialog)
        dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
    else:
        dlg.set_position (gtk.WIN_POS_CENTER)
    dlg.set_modal(gtk.TRUE)
    dlg.show_all()
    dlg.show_now()

    if not os.access (root + command, os.X_OK):
	raise RuntimeError, command + " can not be run"

    (read, write) = os.pipe()

    childpid = os.fork()
    if (not childpid):
        os.environ["CONSOLETYPE"] = 'serial'
        if (root and root != '/'): os.chroot (root)
        if isinstance(catchfd, tuple):
            for fd in catchfd:
                os.dup2(write, fd)
        else:
            os.dup2(write, catchfd)
	os.close(write)
	os.close(read)

	if closefd != -1:
	    os.close(closefd)

	if stdin:
	    os.dup2(stdin, 0)
	    os.close(stdin)

	if (searchPath):
	    os.execvp(command, argv)
	else:
	    os.execv(command, argv)

	sys.exit(1)
    try:
        os.close(write)

        rc = ""
        s = "1"
        while (s):
            try:
                (fdin, fdout, fderr) = select.select([read], [], [], 0.1)
            except:
                fdin = []
                pass

            while gtk.events_pending():
                gtk.mainiteration()

            if __cancelPressed or __dialogClosed:
                raise CancelException
            
            if len(fdin):
                s = os.read(read, 1024)
                rc = rc + s
                iter = buffer.get_end_iter()
                buffer.insert(iter, str(s))
                vadj = swindow.get_vadjustment()
                if vadj.value + vadj.page_size >= vadj.upper - 5:
                    textview.scroll_mark_onscreen(mark)
                
    except CancelException:
        os.kill(childpid, 15)
    except Exception, e:
        os.kill(childpid, 15)
        raise e
        
    os.close(read)
    
    try:
        (pid, status) = os.waitpid(childpid, 0)
    except OSError, (errno, msg):
        #print __name__, "waitpid:", msg
        pass

    if os.WIFEXITED(status) and (os.WEXITSTATUS(status) == 0):
        status = os.WEXITSTATUS(status)
    else:
        status = -1

    if status:
        img = xml.get_widget("statusImage")
        if img:
            img.set_from_stock("gtk-dialog-error", 6)
        if errlabel:
            lbl.set_text(errlabel)
        else:
            lbl.set_text(_("Failed to run:\n%s") % string.join(argv))

    elif len(s):
        lbl.set_text(label + _("\nSucceeded. Please read the output."))        
        
    if (status or len(s)) and not __dialogClosed:
        okbutton.set_sensitive (gtk.TRUE)
        cancelbutton.set_sensitive (gtk.FALSE)
        dlg.run()
        
    dlg.hide()
    return (status, rc)

__xmlfile = None

def __on_okbutton_clicked(*args):
    pass

def __on_cancelbutton_clicked(*args):
    global __cancelPressed
    __cancelPressed = 1
    
def __on_Dialog_close(*args):
    global __dialogClosed
    __dialogClosed = 1
    
def __getXmlFile():
    global __xmlfile
    import os
    if __xmlfile:
        return __xmlfile
    
    glade_file = "infodialog.glade"
    
    if not os.path.isfile(glade_file):
        glade_file = GLADEPATH + glade_file
    if not os.path.isfile(glade_file):
        glade_file = NETCONFDIR + glade_file
            
    __xmlfile = gtk.glade.XML(glade_file, None, domain=PROGNAME)
    return __xmlfile

set_generic_run_dialog_func(gui_run_dialog)
set_generic_run_func(gui_run)

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/10/28 10:18:52 $"
__version__ = "$Revision: 1.29 $"
