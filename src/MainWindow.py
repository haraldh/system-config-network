#!/usr/bin/python

import signal
import gnome.ui
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade

import os
import glob

from ConfiguredDevice import *
from Conf import ConfShellVar

class MainWindow:
    def __init__(self):
        self._cDevList = []
        
        xml = libglade.GladeXML('mainwindow.glade', 'mainWindow')

        # get the widgets we need
        self.toplevel = xml.get_widget("mainWindow")
        self.deviceList = xml.get_widget("deviceList")
        
        xml.signal_autoconnect (
            { "on_closeButton_clicked": self.on_closeButton_clicked,
              }
            )
        
        self.toplevel.connect("delete-event", gtk.mainquit)
        self.toplevel.connect("hide", gtk.mainquit)

        pmenu = xml.get_widget("profileMenu")
        pmenu.remove_menu()
        menu = gtk.GtkMenu()
        for p in self.profileList():
            item = gtk.GtkMenuItem(p)
            item.show()
            item.connect("activate", self.updateDisplay, p)
            menu.append(item)
        pmenu.set_menu(menu)
        pmenu.set_history(self.profileList().index(self.currentProfile()))
        self.updateDisplay(None, self.currentProfile())

        self.toplevel.show_all ()

    def on_closeButton_clicked (self, *args):
        gtk.mainquit ()


    def updateDisplay(self, menuItem, profile):
        self.readConfiguredDevices(profile)
        for cDev in self._cDevList:
            print "Description: %s" % cDev.description()
            print "ID: %s" % cDev.identifier()
            print "isEnabled: %s" % cDev.isEnabled()
            print "name: %s" % cDev.name()
            print "type: %s" % cDev.type()
            print
            print cDev.toString()
            
    
    def profileList(self):
        pList = []
        for f in glob.glob("/etc/sysconfig/networking/*"):
            if os.path.isdir(f):
                pList.append(os.path.basename(f))

        return pList
                

    def devicesInProfile(self, profile):
        return glob.glob("/etc/sysconfig/networking/%s/ifcfg-*" % profile)
    
    def currentProfile(self):
        if os.environ.has_key("CURRENT_PROFILE"):
            return os.environ["CURRENT_PROFILE"]
        else:
            network = ConfShellVar("/etc/sysconfig/networking/network")
            if network.has_key("DEFAULT_PROFILE"):
                return network["DEFAULT_PROFILE"]
            else:
                return "default"

    def readConfiguredDevices(self, profile):
        """
        Reads all configured devices for the selected profile.
        """
        self._cDevList = []
        
        for f in self.devicesInProfile(profile):
            cDev = ConfiguredDevice()
            try:
                cDev.readFile(f)
            except IOError, e:
                dlg = gnome.ui.GnomeErrorDialog("One of the configuration files could not be read:\n%s" % e)
                dlg.run_and_close()
            else:
                self._cDevList.append(cDev)

    
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = MainWindow()
    gtk.mainloop ()
    
