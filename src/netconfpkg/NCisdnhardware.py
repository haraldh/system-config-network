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

import os
import signal
import string
import commands
import sys

card = {
    # "ISDN Adapter" : [ type, irq, io, io1, io2, mem, pci_id, firmware, module ]
    "ACER P10" : [ "30", "5", "0x300", "", "", "", "", "", "hisax" ],
    "ASUS COM ISDNLink ISA PnP" : [ "12", "5", "0x200", "", "", "", "", "", "hisax" ],
    "ASUS COM ISDNLink PCI" : [ "35", "", "", "", "", "", "","", "hisax" ],
    "AVM A1 (Fritz)" : [ "5", "10", "0x300", "", "", "", "","",  "hisax" ],
    "AVM Fritz Card PCMCIA" : [ "", "", "", "", "", "", "", "", "avma1_cs" ],
    "AVM PCI (Fritz!PCI)" : [ "27", "", "", "", "", "", "1244:0a00", "", "hisax" ],
    "AVM PnP" : [ "27", "5", "0x300", "", "", "", "", "", "hisax" ],
    "Billion ISDN P&P PCI 128k Cologne SE" : [ "35", "", "", "", "", "", "1397:2bd0", "", "hisax" ],
    "Compaq ISDN S0 ISA" : [ "19", "5", "0x0000", "0x0000", "0x0000", "", "", "", "hisax" ],
    "Creatix Teles PnP" : [ "4", "5", "0x0000", "0x0000", "", "", "", "", "hisax" ],
    "Dr. Neuhaus Niccy PnP" : [ "24", "5", "", "0x0000", "0x0000", "", "", "", "hisax" ],
    "Dr. Neuhaus Niccy PCI" : [ "24", "", "", "", "", "", "1267:1016", "", "hisax" ],
    "Dynalink 128PH PCI" : [ "36", "", "", "", "", "", "", "", "hisax" ],
    "Eicon.Diehl Diva ISA PnP" : [ "11", "9", "0x180", "", "", "", "", "", "hisax" ],
    "Eicon.Diehl Diva 20PRO PCI" : [ "11", "", "", "", "", "", "1133:e001", "", "hisax" ],
    "Eicon.Diehl Diva 20 PCI" : [ "11", "", "", "", "", "", "1133:e002", "", "hisax" ],
    "Eicon.Diehl Diva 20PRO_U PCI" : [ "11", "", "", "", "", "", "1133:e003", "", "hisax" ],
    "Eicon.Diehl Diva 20_U PCI" : [ "11", "", "", "", "", "", "1133:e004", "", "hisax" ],
    "ELSA PCC/PCF" : [ "6", "", "", "", "", "", "", "", "hisax" ],
    "ELSA Quickstep 1000" : [ "7", "5", "0x300", "", "", "", "", "", "hisax" ],
    "ELSA Quickstep 1000 PCI" : [ "18", "", "", "", "", "", "1048:1000", "", "hisax" ],
    "ELSA Quickstep 3000 PCI" : [ "18", "", "", "", "", "", "1048:3000", "", "hisax" ],
    "ELSA PCMCIA MicroLink cards" : [ "", "", "", "", "", "", "", "", "elsa_cs" ],
    "Gazel cards ISA" : [ "34", "5", "0x300", "", "", "", "", "", "hisax" ],
    "Gazel cards PCI" : [ "34", "", "", "", "", "", "10b5:1030", "", "hisax" ],
    "HFC-2BS0 based cards ISA" : [ "13", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "HFC-2BS0 based cards PCI" : [ "35", "", "", "", "", "", "1397:2bd0", "", "hisax" ],
    "HST Saphir" : [ "31", "5", "0x300", "", "", "", "", "", "hisax" ],
    "ITK ix1-micro Rev.2" : [ "9", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "MIC card" : [ "17", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "NETjet PCI" : [ "20", "", "", "", "", "", "e159:0001", "", "hisax" ],
    "Sedlbauer PC 104" : [ "15", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "Sedlbauer Speed PCI" : [ "15", "", "", "", "", "", "", "", "hisax" ],
    "Sedlbauer Speed Card" : [ "15", "9", "0xd80", "", "", "", "", "", "hisax" ],
    "Sedlbauer Speed Fax+" : [ "28", "9", "0xd80", "", "", "", "", "hisaxctrl HiSax 9 /usr/lib/isdn/ISAR.BIN", "hisax" ],
    "Sedlbauer Speed fax+ PCI" : [ "28", "", "", "", "", "", "e159:0002", "hisaxctrl HiSax 9 /usr/lib/isdn/ISAR.BIN", "hisax" ],
    "Sedlbauer Speed Star PCMCIA Card" : [ "", "", "", "", "", "", "", "", "sedlbauer_cs" ],
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
    "W6692 based PCI cards" : [ "36", "", "", "", "", "", "1050:6692", "", "hisax" ]
    }


class ConfISDN:
    def __init__(self):
        self.Id = "HiSax"
        self.Description = ""
        self.ChannelProtocol = "2"
        self.Type = ""
        self.IRQ = ""
        self.IoPort = ""
        self.IoPort1 = ""
        self.IoPort2 = ""
        self.Mem = ""
        self.Pci_id = ""
        self.Firmware = ""
        self.ModuleName = "hisax"

    def get_value(self, s):
        if string.find(s, "=") < 0:
            return ""
        s = string.split(s, "=", 1)[1]
        s = string.replace(s, "\"", "")

        return string.strip(s)

    def load(self, f = "/etc/sysconfig/isdncard"):
        if not os.path.exists(f):
            return -1

        conf = open(f, "r")
        line = conf.readline()

        while line:
            line = string.strip(line)
            if len(line) == 0 or line[0] == "#":
                pass
            elif line[:5]  == "NAME=":
                self.Description = self.get_value(line)
            elif line[:7] == "MODULE=":
                self.ModuleName = self.get_value(line)
            elif line[:9] == "FIRMWARE=":
                self.Firmware = self.get_value(line)
            elif line[:10] == "RESOURCES=":
                rlist = string.split(self.get_value(line), " ")
                for i in rlist:
                    if string.find(i, "type=") == 0:
                        self.Type = self.get_value(i)
                    elif string.find(i, "protocol=") == 0:
                        self.ChannelProtocol = self.get_value(i)
                    elif string.find(i, "irq=") == 0:
                        self.IRQ = self.get_value(i)
                    elif string.find(i, "id=") == 0:
                        self.Id = self.get_value(i)
                    elif string.find(i, "io=") == 0 or string.find(i, "io0=") == 0:
                        self.IoPort = self.get_value(i)
                    elif string.find(i, "io1=") == 0:
                        self.IoPort1 = self.get_value(i)
                    elif string.find(i, "io2=") == 0:
                        self.IoPort2 = self.get_value(i)
                    elif string.find(i, "mem=") == 0:
                        self.Mem = self.get_value(i)
            line = conf.readline()
            
        conf.close()
        return 1
    
    def save(self, f = "/etc/sysconfig/isdncard"):
        # we only support 1 ISDN card in this version
        if not self.Description:
            if  os.path.exists(f):
                os.unlink(f)
            return

        try:
            conf = open( f, "w")
            conf.write("NAME=\"" + self.Description + "\"\n")
            conf.write("MODULE=\"" + self.ModuleName + "\"\n")
            if self.Firmware:
                conf.write("FIRMWARE=\"" + self.Firmware + "\"\n")

            rs = "RESOURCES=\""
            if self.Type:
                rs = rs + "type=" + str(self.Type) + " protocol=" + str(self.ChannelProtocol)
                if self.IRQ:
                    rs = rs + " irq=" + str(self.IRQ)
                if self.Id:
                    rs = rs + " id=" + str(self.Id)
                if self.IoPort:
                    if self.Type == "4" or self.Type == "19" or self.Type == "24":
                        rs = rs + " io0=" + str(self.IoPort)
                    else:
                        rs = rs + " io=" + str(self.IoPort)
                if self.IoPort1:
                    rs = rs + " io1=" + str(self.IoPort1)
                if self.IoPort2:
                    rs = rs + " io2=" + str(self.IoPort2)
                if self.Mem:
                    rs = rs + " mem=" + str(self.Mem)
            else:
                rs = rs + "NONE"

            rs = rs + "\"\n"
            conf.write(rs)
            conf.close()
            
        except(IOError): pass

    def detect(self):
        f = '/sbin/lspci'
        if not os.path.exists(f): return
        
        line = commands.getoutput(f + ' -n 2>/dev/null')
        for i in card.keys():
            if len(card[i][6]) >0 and string.find(line, card[i][6])>0:
                return {i : card[i]}

    def get_resource(self, name):
        if card.has_key(name):
            self.Description = name
            self.Type = card[name][0]
            self.IRQ = card[name][1]
            self.IoPort = card[name][2]
            self.IoPort1 = card[name][3]
            self.IoPort2 = card[name][4]
            self.Mem = card[name][5]
            self.Pci_id = card[name][6]
            self.Firmware = card[name][7]
            self.ModuleName = card[name][8]


if __name__ == "__main__":
    conf = ConfISDN()
    if conf.load() < 0:
        new_card = conf.detect()
        if new_card:
            conf.get_resource(new_card.keys()[0])
        else:
            print "not found:"
            sys.exit(0)

    print "Channel Protocol: ", conf.ChannelProtocol
    print "Name: ", conf.Description
    print "Type: ", conf.Type
    print "Irq: ", conf.IRQ
    print "Io: ", conf.IoPort
    print "Io1: ", conf.IoPort1
    print "Io2: ", conf.IoPort2
    print "Mem: ", conf.Mem
    print "Pci id: ", conf.Pci_id
    print "Firmware: ", conf.Firmware
    print "Modul: ", conf.ModuleName
    print "ID: ", conf.Id

