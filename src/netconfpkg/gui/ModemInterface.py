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
from netconfpkg.gui.GUI_functions import *
from netconfpkg.gui import GUI_functions
from netconfpkg import *
from netconfpkg import *
import gtk
from gtk import TRUE
from gtk import FALSE
import gtk.glade
import string
import os
import time
import providerdb
import gtk.glade
import DialupDruid
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect


class ModemInterface:
    modemList = None
    def __init__ (self, toplevel=None, do_save = 1, druid = None):
        self.do_save = do_save
        glade_file = 'ModemDruid.glade'

        if not os.path.isfile(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file
 
        self.xml = gtk.glade.XML(glade_file, 'druid', domain=GUI_functions.PROGNAME)
        xml_signal_autoconnect(self.xml,
            {
            "on_Modem_prepare" : self.on_Modem_prepare,
            "on_Modem_back" : self.on_Modem_back,
            "on_Modem_next" : self.on_Modem_next,
            })
        
        self.toplevel = toplevel
        self.hardwarelist = NCHardwareList.getHardwareList()
        self.hw = None
        self.druids = []
        
        druid = self.xml.get_widget('druid')
        for I in druid.get_children():
            druid.remove(I)
            self.druids.append(I)

        self.setup()
        
    def get_project_name(self):
        return _('Modem connection')

    def get_type(self):
        return MODEM

    def get_project_description (self):
        return _("Create a new Modem connection.  This is a connection that uses a "
                 "serial analog modem to dial into to your Internet Service Provider. "
                 "These modems use sound over a normal copper telephone line to transmit "
                 "data.  These types of connections are available just about anywhere in "
                 "the world where there is a phone system.")


    def get_druids(self):
        Type = MODEM
        dialup = DialupDruid.DialupDruid(self.toplevel, Type,
                                         do_save = self.do_save)
        for self.hw in self.hardwarelist:
            if self.hw.Type == Type: return dialup.get_druids()
 
        id = self.hardwarelist.addHardware(Type)
        self.hw = self.hardwarelist[id]
        self.hw.Type = Type
        self.hw.Name = Type + '0'
        if Type == 'ISDN':  self.hw.createCard()
        elif Type == 'Modem': self.hw.createModem()
 
        return self.druids[0:] + dialup.get_druids()

    def on_Modem_prepare(self, druid_page, druid):
        if not ModemInterface.modemList:
            dialog = gtk.Dialog(_('Modem probing...'),
                                None,
                                gtk.DIALOG_MODAL|gtk.DIALOG_NO_SEPARATOR|gtk.DIALOG_DESTROY_WITH_PARENT)
            dialog.set_border_width(10)
            label = gtk.Label(_('Probing for Modems, please wait...'))
            dialog.vbox.pack_start(label, gtk.FALSE)
            dialog.set_transient_for(self.toplevel)
            dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            dialog.set_modal(TRUE)
            label.show_now()
            dialog.show_all()
            dialog.show_now()
            gtk.gdk.flush()
            while gtk.events_pending():
                gtk.main_iteration(gtk.FALSE)
            dlist = GUI_functions.getModemList()
            ModemInterface.modemList = dlist
            dialog.destroy()
            if dlist == []:
                generic_error_dialog(_('No modem was found on your system.'),
                                     self.toplevel)
                dlist = modemDeviceList
            ModemInterface.modemList = dlist
        else:
            dlist = ModemInterface.modemList

        self.xml.get_widget("modemDeviceEntryComBo").set_popdown_strings(dlist)
        # 460800 seems to be to high
        self.xml.get_widget("baudrateEntry").set_text("57600")
 
    def on_Modem_next(self, druid_page, druid):
        self.dehydrate()
 
    def on_Modem_back(self, druid_page, druid):
        self.hardwarelist.rollback()
        
    def setup(self):
        pass

    def dehydrate(self):
        self.hw.Description = _('Generic Modem')
        self.hw.Modem.DeviceName = self.xml.get_widget("modemDeviceEntry").get_text()
        if len(self.hw.Modem.DeviceName)>5 and self.hw.Modem.DeviceName[:5] != '/dev/':
            self.hw.Modem.DeviceName = '/dev/' + self.hw.Modem.DeviceName
        self.hw.Modem.BaudRate = int(self.xml.get_widget("baudrateEntry").get_text())
        self.hw.Modem.FlowControl = self.xml.get_widget("flowControlEntry").get_text()
        Item = self.xml.get_widget("volumeMenu").get_child().get_label()
        if Item == _("Off"):
            self.hw.Modem.ModemVolume = 0
        elif Item == _("Low"):
            self.hw.Modem.ModemVolume = 1
        elif Item == _("Medium"):
            self.hw.Modem.ModemVolume = 2
        elif Item == _("High"):
            self.hw.Modem.ModemVolume = 3
        elif Item == _("Very High"):
            self.hw.Modem.ModemVolume = 4
        else:
            self.hw.Modem.ModemVolume = 0
 
        if self.xml.get_widget("toneDialingCB").get_active():
            self.hw.Modem.DialCommand = "ATDT"
        else:
            self.hw.Modem.DialCommand = "ATDP"

    def hydrate(self):
        hardwarelist = NCHardwareList.getHardwareList()

        if self.hw.Modem.DeviceName != None:
            if not self.hw.Modem.DeviceName in modemDeviceList:
                modemDeviceList.insert(0, self.hw.Modem.DeviceName)
                self.xml.get_widget("modemDeviceEntryCombo").set_popdown_strings(modemDeviceList)
            self.xml.get_widget('modemDeviceEntry').set_text(self.hw.Modem.DeviceName)
        if self.hw.Modem.BaudRate != None:
            self.xml.get_widget('baudrateEntry').set_text(str(self.hw.Modem.BaudRate))
        if self.hw.Modem.FlowControl != None and modemFlowControls.has_key(self.hw.Modem.FlowControl):
            self.xml.get_widget('flowControlEntry').set_text(modemFlowControls[self.hw.Modem.FlowControl])

NCDevModem.setDevModemWizard(ModemInterface)
