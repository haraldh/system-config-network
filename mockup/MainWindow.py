#!/usr/bin/python

import signal
import gnome.ui
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade

class MainWindow:
    def __init__(self):
        self.creator = None
        xml = libglade.GladeXML('mainwindow.glade', 'mainWindow')

        # get the widgets we need
        self.toplevel = xml.get_widget("mainWindow")
        self.deviceList = xml.get_widget("deviceList")
        
        xml.signal_autoconnect (
            { })


        self.toplevel.show_all ()

    def on_cancel_interface (self, *args):
        gtk.mainquit ()

if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = MainWindow()
    gtk.mainloop ()
    
