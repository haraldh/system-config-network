## Copyright (C) 2001, 2002 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001, 2002 Harald Hoyer <harald@redhat.com>
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

gtk.glade.bindtextdomain(PROGNAME, "/usr/share/locale")

GLADEPATH='netconfpkg/gui/'

DEVPIXMAPS = {}

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

def get_icon(pixmap_file, dialog):
    pixbuf = get_pixbuf(pixmap_file)
    
    pix, mask = pixbuf.render_pixmap_and_mask()
    
    #pix, mask = gtk.create_pixmap_from_xpm(dialog, None, pixmap_file)
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
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)

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
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)

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
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        
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
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)

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

def growToParent(widget, rect, growTo=None):
    return
    if not widget.parent:
        return
    ignore = widget.__dict__.get("ignoreEvents")
    if not ignore:
        if growTo:
            x, y, width, height = growTo.get_allocation()
            widget.set_size_request(width, -1)
        else:
            widget.set_size_request(rect.width, -1)
        widget.ignoreEvents = 1
    else:
        widget.ignoreEvents = 0

def widgetExpander(widget, growTo=None):
    widget.connect("size-allocate", growToParent, growTo)

class WrappingLabel(gtk.Label):
    def __init__(self, label=""):
        gtk.Label.__init__(self, label)
        self.set_line_wrap(gtk.TRUE)
        self.ignoreEvents = 0
#        self.set_size_request(-1, 1)
        widgetExpander(self)
