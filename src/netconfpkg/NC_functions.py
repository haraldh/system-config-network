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

import re
import traceback
import sys
import os
import os.path
import shutil
import gettext
import ConfPAP
#import gnome
#import gnome.ui

true = (1==1)
false = not true

PROGNAME='redhat-config-network'
NETCONFDIR='/usr/share/redhat-config-network/'
OLDSYSCONFDEVICEDIR='/etc/sysconfig/network-scripts/'
SYSCONFDEVICEDIR='/etc/sysconfig/networking/devices/'
SYSCONFPROFILEDIR='/etc/sysconfig/networking/profiles/'
SYSCONFNETWORK='/etc/sysconfig/network'

gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
_ = gettext.gettext

ETHERNET = 'Ethernet'
MODEM = 'Modem'
ISDN = 'ISDN'
LO = 'Loopback'
DSL = 'xDSL'
CIPE = 'CIPE'
WIRELESS = 'Wireless'
TOKENRING = 'Token Ring'
CTC = 'CTC'
IUCV = 'IUCV'

deviceTypes = [ ETHERNET, MODEM, ISDN, LO, DSL, CIPE, WIRELESS, TOKENRING, CTC, IUCV ]

modemDeviceList = [ '/dev/modem', '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3',
		    '/dev/ttyI0', '/dev/ttyI1', '/dev/ttyI2', '/dev/ttyI3' ]

ctcDeviceList = [ 'ctc0', 'ctc1', 'ctc2', 'ctc3', 'ctc4' ]

iucvDeviceList = [ 'iucv0', 'iucv1', 'iucv2', 'iucv3', 'iucv4' ]

deviceTypeDict = { '^eth[0-9]+(:[0-9]+)?$' : ETHERNET,
		   '^ppp[0-9]+(:[0-9]+)?$' : MODEM,
		   '^ippp[0-9]+(:[0-9]+)?$' : ISDN,
		   '^cipcb[0-9]+(:[0-9]+)?$' : CIPE,
		   '^tr[0-9]+(:[0-9]+)?$' :TOKENRING,
		   '^lo$' : LO,
		   '^ctc[0-9]+(:[0-9]+)?$' : CTC,
		   '^iucv[0-9]+(:[0-9]+)?$' : IUCV
		   }

class TestError(Exception):
	def __init__(self, args=None):
		self.args = args


DVpapconf = None
def getPAPConf():
    global DVpapconf
    if DVpapconf == None:        
        DVpapconf = ConfPAP.ConfPAP("/etc/ppp/pap-secrets")
    return DVpapconf

DVchapconf = None
def getCHAPConf():
    global DVchapconf
    if DVchapconf == None:
        DVchapconf = ConfPAP.ConfPAP("/etc/ppp/chap-secrets")
    return DVchapconf

def create_ethernet_combo(hardwarelist, devname):
        hwdesc = [ 'eth0', 'eth1', 'eth2',
                   'eth3', 'eth4', 'eth5',
                   'eth6', 'eth7', 'eth8'
                   ]
        hwcurr = None
        
        for hw in hardwarelist:
            if hw.Type == ETHERNET:
                desc = str(hw.Name) + ' (' + hw.Description + ')'
                try:
                    i = hwdesc.index(hw.Name)
                    hwdesc[i] = desc
                except:
                    hwdesc.append(desc)
                    
                if devname and hw.Name == devname:
                    hwcurr = desc
                    
        if not hwcurr:
            if devname:
                hwcurr = devname
            elif len(hwdesc):
                hwcurr = hwdesc[0]

        hwdesc.sort()
        
        return (hwcurr, hwdesc[:])

def create_tokenring_combo(hardwarelist, devname):
        hwdesc = [ 'tr0', 'tr1', 'tr2',
                   'tr3', 'tr4', 'tr5',
                   'tr6', 'tr7', 'tr8'
                   ]
        hwcurr = None
        
        for hw in hardwarelist:
            if hw.Type == TOKENRING:
                desc = str(hw.Name) + ' (' + hw.Description + ')'
                try:
                    i = hwdesc.index(hw.Name)
                    hwdesc[i] = desc
                except:
                    hwdesc.append(desc)
                    
                if devname and hw.Name == devname:
                    hwcurr = desc
                    
        if not hwcurr:
            if devname:
                hwcurr = devname
            elif len(hwdesc):
                hwcurr = hwdesc[0]

        hwdesc.sort()
        
        return (hwcurr, hwdesc[:])

def ishardlink(file):
    return os.stat(file)[3] > 1


def getDeviceType(devname):
    type = 'Unknown'
    if not devname or devname == "":
        return type
    
    for i in deviceTypeDict.keys():
        if re.search(i, devname):
            type = deviceTypeDict[i]
    return type

def updateNetworkScripts():
    if not os.path.isdir(SYSCONFDEVICEDIR):
        os.mkdir(SYSCONFDEVICEDIR)

    if not os.path.isdir(SYSCONFPROFILEDIR):
        os.mkdir(SYSCONFPROFILEDIR)

    if not os.path.isdir(SYSCONFPROFILEDIR+'/default/'):
        os.mkdir(SYSCONFPROFILEDIR+'/default/')

    devlist = os.listdir(OLDSYSCONFDEVICEDIR)
    for dev in devlist:
        if dev[:6] != 'ifcfg-' or dev == 'ifcfg-lo':
            continue

        if os.path.islink(OLDSYSCONFDEVICEDIR+'/'+dev) or ishardlink(OLDSYSCONFDEVICEDIR+'/'+dev):
            #print dev+" already a link, skipping it."
            continue

        if getDeviceType(dev[6:]) == 'Unknown':
            #print dev+" has unknown device type, skipping it."
            continue

        print "Copying "+dev+" to devices and putting it into the default profile."

        try:
            os.unlink(SYSCONFPROFILEDIR+'/default/'+dev)
        except:
            pass

        try:
            shutil.copy(OLDSYSCONFDEVICEDIR+'/'+dev, SYSCONFDEVICEDIR+'/'+dev)
            os.link(SYSCONFDEVICEDIR+'/'+dev, SYSCONFPROFILEDIR+'/default/'+dev)
#            os.link(SYSCONFPROFILEDIR+'/default/'+dev, OLDSYSCONFDEVICEDIR+'/'+dev)
        except:
            print "An error occured during the conversion of device "+dev+", skipping."
            (type, value, tb) = sys.exc_info()
            list = traceback.format_exception (type, value, tb)
            print list
            continue

    if not ishardlink('/etc/hosts') and not os.path.islink('/etc/hosts'):
       print "Copying /etc/hosts to default profile."
       try:
           shutil.copy('/etc/hosts', SYSCONFPROFILEDIR+'/default/hosts')
       except:
           print "An error occured during moving the /etc/hosts file."

    if not ishardlink('/etc/resolv.conf') and not os.path.islink('/etc/resolv.conf'):
       print "Copying /etc/resolv.conf to default profile."
       try:
           shutil.copy('/etc/resolv.conf', SYSCONFPROFILEDIR+'/default/resolv.conf')
       except:
           print "An error occured during moving the /etc/resolv.conf file."
