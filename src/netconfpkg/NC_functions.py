import gnome
import gnome.ui

OLDSYSCONFDEVICEDIR='/etc/sysconfig/network-scripts/'
SYSCONFDEVICEDIR='/etc/sysconfig/networking/devices/'
SYSCONFPROFILEDIR='/etc/sysconfig/networking/profiles/'

def generic_error_dialog (message, parent_dialog, dialog_type="warning", widget=None, page=0, broken_widget=None):
    dialog = gnome.ui.GnomeMessageBox (message, dialog_type, "Button_Ok")
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
    dialog.run ()

