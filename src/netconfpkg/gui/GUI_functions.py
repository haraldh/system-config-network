import os
import gtk
from gtk import TRUE
from gtk import FALSE
import gnome
import gnome.ui
from netconfpkg.NC_functions import *
from netconfpkg.NC_functions import _

GLADEPATH='netconfpkg/gui/'

def get_icon(pixmap_file, dialog):
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
        return None, None

    pix, mask = gtk.create_pixmap_from_xpm(dialog, None, pixmap_file)
    return pix, mask
 
def load_icon(pixmap_file, dialog):
    if not dialog: return
 
    pix, mask = get_icon(pixmap_file, dialog)
    if not pix: return
 
    gtk.GtkPixmap(pix, mask)
    if dialog: dialog.set_icon(pix, mask)


def generic_error_dialog (message, parent_dialog, dialog_type="warning",
			  widget=None, page=0, broken_widget=None):
    dialog = gnome.ui.GnomeMessageBox (message, dialog_type, "Button_Ok")
    if parent_dialog:
	    dialog.set_parent (parent_dialog)
    if widget != None:
        if isinstance (widget, gtk.GtkCList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.GtkNotebook):
            widget.set_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.GtkEntry):
            broken_widget.select_region (0, -1)

    dialog.set_position (gtk.WIN_POS_MOUSE)
    dialog.run ()

def generic_yesnocancel_dialog (message, parent_dialog, dialog_type="question",
			  widget=None, page=0, broken_widget=None):
    dialog = gnome.ui.GnomeMessageBox (message, dialog_type, _("Yes"), _("No"), _("Cancel"))
    if parent_dialog:
	    dialog.set_parent (parent_dialog)
    if widget != None:
        if isinstance (widget, gtk.GtkCList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.GtkNotebook):
            widget.set_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.GtkEntry):
            broken_widget.select_region (0, -1)
    dialog.set_position (gtk.WIN_POS_MOUSE)
    return dialog.run ()

def generic_yesno_dialog (message, parent_dialog, dialog_type="question",
			  widget=None, page=0, broken_widget=None):
    dialog = gnome.ui.GnomeMessageBox (message, dialog_type, _("Yes"), _("No"))
    if parent_dialog:
	    dialog.set_parent (parent_dialog)
    if widget != None:
        if isinstance (widget, gtk.GtkCList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.GtkNotebook):
            widget.set_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.GtkEntry):
            broken_widget.select_region (0, -1)
    dialog.set_position (gtk.WIN_POS_MOUSE)
    return dialog.run ()
