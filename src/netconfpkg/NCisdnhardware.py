#! /usr/bin/python
 
## netconf - A network configuration tool
## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Than Ngo <than@redhat.com>
 
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

import sys
import signal
import os
import string
import re
 
FALSE = 0
TRUE = not FALSE

card = {
    "ACER P10" : [ "30", "5", "0x300", "", "", "", "", "", "hisax" ],
    "ASUS COM ISDNLink ISA PnP" : [ "12", "5", "0x200", "", "", "", "", "", "hisax" ],
    "ASUS COM ISDNLink PCI" : [ "35", "", "", "", "", "", "","","hisax" ],
    "AVM A1 (Fritz)" : [ "5", "10", "0x300", "", "", "", "","", "hisax" ],
    "AVM PCI (Fritz!PCI)" : [ "27", "", "", "", "", "", "12440a00", "", "hisax" ],
    "AVM PnP" : [ "27", "5", "0x300", "", "", "", "", "", "hisax" ],
    "Compaq ISDN S0 ISA" : [ "19", "5", "0x0000", "0x0000", "0x0000", "", "", "", "hisax" ],
    "Creatix Teles PnP" : [ "4", "5", "0x0000", "0x0000", "", "", "", "", "hisax" ],
    "Dr. Neuhaus Niccy PnP" : [ "24", "5", "", "0x0000", "0x0000", "", "", "", "hisax" ],
    "Dr. Neuhaus Niccy PCI" : [ "24", "", "", "", "", "", "12671016", "", "hisax" ],
    "Dynalink 128PH PCI" : [ "36", "", "", "", "", "", "", "", "hisax" ],
    "Eicon.Diehl Diva ISA PnP" : [ "11", "9", "0x180", "", "", "", "", "", "hisax" ],
    "Eicon.Diehl Diva 20PRO PCI" : [ "11", "", "", "", "", "", "1133e001", "", "hisax" ],
    "Eicon.Diehl Diva 20 PCI" : [ "11", "", "", "", "", "", "1133e002", "", "hisax" ],
    "Eicon.Diehl Diva 20PRO_U PCI" : [ "11", "", "", "", "", "", "1133e003", "", "hisax" ],
    "Eicon.Diehl Diva 20_U PCI" : [ "11", "", "", "", "", "", "1133e004", "", "hisax" ],
    "ELSA PCC/PCF" : [ "6", "", "", "", "", "", "", "", "hisax" ],
    "ELSA Quickstep 1000" : [ "7", "5", "0x300", "", "", "", "", "", "hisax" ],
    "ELSA Quickstep 1000 PCI" : [ "18", "", "", "", "", "", "10481000", "", "hisax" ],
    "ELSA Quickstep 3000 PCI" : [ "18", "", "", "", "", "", "10483000", "", "hisax" ],
    "ELSA PCMCIA MicroLink cards" : [ "0", "", "", "", "", "", "", "", "elsa_cs" ],
    "Gazel cards ISA" : [ "34", "5", "0x300", "", "", "", "", "", "hisax" ],
    "Gazel cards PCI" : [ "34", "", "", "", "", "", "10b51030", "", "hisax" ],
    "HFC-2BS0 based cards ISA" : [ "13", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "HFC-2BS0 based cards PCI" : [ "35", "", "", "", "", "", "13972bd0", "", "hisax" ],
    "HST Saphir" : [ "31", "5", "0x300", "", "", "", "", "", "hisax" ],
    "ITK ix1-micro Rev.2" : [ "9", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "MIC card" : [ "17", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "NETjet PCI" : [ "20", "", "", "", "", "", "e1590001", "", "hisax" ],
    "Sedlbauer PC 104" : [ "15", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "Sedlbauer Speed PCI" : [ "15", "", "", "", "", "", "", "", "hisax" ],
    "Sedlbauer Speed Card" : [ "15", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "Sedlbauer Speed Fax+" : [ "28", "9", "0xd80", "", "", "", "", "hisaxctrl HiSax 9 /usr/lib/isdn/ISAR.BIN", "hisax" ],
    "Sedlbauer Speed fax+ PCI" : [ "28", "", "", "", "", "", "e1590002", "hisaxctrl HiSax 9 /usr/lib/isdn/ISAR.BIN", "hisax" ],
    "Sedlbauer Speed Star PCMCIA Card" : [ "0", "", "", "", "", "", "", "", "sedlbauer_cs" ],
    "Siemens I-Surf 1.0" : [ "29", "9", "0xd80", "", "", "0xd000", "", "", "hisax" ],
    "Telekom A4T" : [ "32", "", "", "", "", "", "", "", "hisax" ],
    "Teles 8.0" : [ "2", "9", "", "", "", "0xd800", "", "", "hisax" ],
    "Teles 16.0" : [ "1", "5", "0xd80", "", "", "0xd000", "", "", "hisax" ],
    "Teles 16.3" : [ "3", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "Teles 16.3c PnP" : [ "14", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "Teles PCI" : [ "21", "", "", "", "", "", "", "", "hisax" ],
    "Teles PnP" : [ "4", "5", "0x0000", "0x0000", "", "", "", "", "hisax" ],
    "Teles S0Box" : [ "25", "7", "0x378", "", "", "", "", "", "hisax" ],
    "USR Sportster intern" : [ "16", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "W6692 based PCI cards" : [ "36", "", "", "", "", "", "10506692", "", "hisax" ]
    }
    
    
class ISDNResource:
    def __init__(self, name):
        self.name = name

    def get_type(self):
        if card.has_key(self.name):
            return card[self.name][0]

    def get_irq(self):
        if card.has_key(self.name):
            return card[self.name][1]

    def set_irq(self, irq):
        if card.has_key(self.name):
            self.irq = irq

    def get_io(self):
        if card.has_key(self.name):
            return card[self.name][2]

    def set_io(self, io):
        if card.has_key(self.name):
            self.io = io

    def get_io1(self):
        if card.has_key(self.name):
            return card[self.name][3]

    def set_io1(self, io1):
        if card.has_key(self.name):
            self.io1 = io1

    def get_io2(self):
        if card.has_key(self.name):
            return card[self.name][4]

    def set_io2(self, io2):
        if card.has_key(self.name):
            self.io2 = io2

    def get_mem(self):
        if card.has_key(self.name):
            return card[self.name][5]

    def set_mem(self, mem):
        if card.has_key(self.name):
            self.mem = mem

    def get_pci_id(self):
        if card.has_key(self.name):
            return card[self.name][6]

    def get_firmware(self):
        if card.has_key(self.name):
            return card[self.name][7]

    def get_modul(self):
        if card.has_key(self.name):
            return card[self.name][8]


if __name__ == "__main__":
    name = "Sedlbauer Speed PCI"
    isdncard = ISDNResource(name);
    print "Name: ", name
    print "Type: ", isdncard.get_type()
    print "Irq: ", isdncard.get_irq()
    print "Io: ", isdncard.get_io()
    print "Io1: ", isdncard.get_io1()
    print "Io2: ", isdncard.get_io2()
    print "Mem: ", isdncard.get_mem()
    print "Pci id: ", isdncard.get_pci_id()
    print "Firmware: ", isdncard.get_firmware()
    print "Modul: ", isdncard.get_modul()

