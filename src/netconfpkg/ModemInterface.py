## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Than Ngo <than@redhat.com>
## Copyright (C) 2001 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001 Philipp Knirsch <pknirsch@redhat.com>

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

import NC_functions
from NC_functions import _
import NCHardwareList
import NCisdnhardware
import kudzu
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade
import string
import os
import time
import providerdb
import libglade
import DialupDruid


class ModemInterface:
    def __init__ (self, toplevel=None):
        glade_file = 'ModemDruid.glade'

        if not os.path.isfile(glade_file):
            glade_file = 'netconfpkg/' + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NC_functions.NETCONFDIR + glade_file
 
        self.xml = libglade.GladeXML(glade_file, 'druid', domain=NC_functions.PROGNAME)
        self.xml.signal_autoconnect(
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
        for I in druid.children():
            druid.remove(I)
            self.druids.append(I)

        self.setup()
        
    def get_project_name(self):
        return _('Modem connection')

    def get_project_description (self):
        return _('Create a new Modem connection.  The dialup interface is used primarily for connecting to an ISP over a modem.')

    def get_druids(self):
        Type = 'Modem'
        dialup = DialupDruid.DialupDruid(self.toplevel, Type)
        for self.hw in self.hardwarelist:
            if self.hw.Type == Type: return dialup.get_druids()
 
        id = self.hardwarelist.addHardware()
        self.hw = self.hardwarelist[id]
        self.hw.Type = Type
        self.hw.Name = Type + '0'
        if Type == 'ISDN':  self.hw.createCard()
        elif Type == 'Modem': self.hw.createModem()
 
        return self.druids[0:] + dialup.get_druids()

    def on_Modem_prepare(self, druid_page, druid):
        pass
 
    def on_Modem_next(self, druid_page, druid):
        self.dehydrate()
 
    def on_Modem_back(self, druid_page, druid):
        self.hardwarelist.rollback()
        
    def setup(self):
        dialog = gtk.GtkWindow(gtk.WINDOW_DIALOG, 'Modem probing...')
        dialog.set_border_width(10)
        vbox = gtk.GtkVBox(1)
        vbox.add(gtk.GtkLabel('Probing for Modems, please wait...'))
        dialog.add(vbox)
        dialog.show_all()
        while gtk.events_pending():
            gtk.mainiteration(FALSE)
        time.sleep(1)
        res = kudzu.probe(kudzu.CLASS_MODEM, kudzu.BUS_SERIAL|kudzu.BUS_PCI, kudzu.PROBE_ALL)
        if res == []:
            dlist = ['/dev/modem']
        else:
            dlist = []
            for v in res:
                dev = str(v[0])
                if dev != 'None':
                    dlist.append(dev)
        dialog.destroy()
        self.xml.get_widget("modemDeviceEntryComBo").set_popdown_strings(dlist)
    
    def dehydrate(self):
        self.hw.Description = _('Generic Modem')
        self.hw.Modem.DeviceName = self.xml.get_widget("modemDeviceEntry").get_text()
        self.hw.Modem.BaudRate = string.atoi(self.xml.get_widget("baurateEntry").get_text())
        self.hw.Modem.FlowControl = self.xml.get_widget("flowControlEntry").get_text()
        Item = self.xml.get_widget("volumeMenu")["label"]
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
 
        if self.xml.get_widget("toneDialingCB")["active"]:
            self.hw.Modem.DialCommand = "ATDT"
        else:
            self.hw.Modem.DialCommand = "ATDP"
