## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
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

import re
import traceback
import sys
import os
import os.path
import shutil
from rhpl import ConfPAP
from rhpl import ethtool

true = (1==1)
false = not true


PROGNAME = "redhat-config-network"

NETCONFDIR='/usr/share/redhat-config-network/'
OLDSYSCONFDEVICEDIR='/etc/sysconfig/network-scripts/'
SYSCONFDEVICEDIR='/etc/sysconfig/networking/devices/'
SYSCONFPROFILEDIR='/etc/sysconfig/networking/profiles/'
SYSCONFNETWORK='/etc/sysconfig/network/'

import gettext
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
try:
    gettext.install(PROGNAME, "/usr/share/locale", 1)
except IOError:
    import __builtin__
    __builtin__.__dict__['_'] = unicode    

DEFAULT_PROFILE_NAME=_("Common")

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

modemDeviceList = [ '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3',
		    '/dev/ttyI0', '/dev/ttyI1', '/dev/ttyI2', '/dev/ttyI3',
		    '/dev/input/ttyACM0', '/dev/input/ttyACM1',
		    '/dev/input/ttyACM2', '/dev/input/ttyACM3',
		    '/dev/ttyM0', '/dev/ttyM1' ]

ctcDeviceList = [ 'ctc0', 'ctc1', 'ctc2', 'ctc3', 'ctc4' ]

iucvDeviceList = [ 'iucv0', 'iucv1', 'iucv2', 'iucv3', 'iucv4' ]

deviceTypeDict = { '^eth[0-9]*(:[0-9]+)?$' : ETHERNET,
		   '^ppp[0-9]*(:[0-9]+)?$' : MODEM,
		   '^ippp[0-9]*(:[0-9]+)?$' : ISDN,
		   '^isdn[0-9]*(:[0-9]+)?$' : ISDN,
		   '^cipcb[0-9]*(:[0-9]+)?$' : CIPE,
		   '^tr[0-9]*(:[0-9]+)?$' :TOKENRING,
		   '^lo$' : LO,
		   '^ctc[0-9]*(:[0-9]+)?$' : CTC,
		   '^iucv[0-9]*(:[0-9]+)?$' : IUCV,
		   }
# Removed for now, until we have a config dialog for infrared
#		   '^irlan[0-9]+(:[0-9]+)?$' : WIRELESS


CRTSCTS = "CRTSCTS"
XONXOFF = "XONXOFF"
NOFLOW = "NOFLOW"

modemFlowControls = { CRTSCTS : _("Hardware (CRTSCTS)"),
		      XONXOFF : _("Software (XON/XOFF)"),
		      NOFLOW :  _("None") } 


def nop(*args):
    pass

class TestError(Exception):
    def __init__(self, args=None):
        self.args = args


def rpms_notinstalled(namelist):
    import rpm
    
    ts = rpm.TransactionSet("/")
    ts.setVSFlags(rpm.RPMVSF_NORSA|rpm.RPMVSF_NODSA)
    ts.setFlags(rpm.RPMTRANS_FLAG_NOMD5)

    if len(namelist) == 0:
        namelist = [ namelist ]

    toinstall = namelist[:]
   
    for name in namelist:
        mi = ts.dbMatch('name', name)
        for n in mi:
            print n[rpm.RPMTAG_NAME]
            if n[rpm.RPMTAG_NAME] == name:
                toinstall.remove(name)
                break
                
    del (ts)
    return toinstall

def assure_rpms(pkgs = []):
    toinstall = rpms_notinstalled(pkgs)

    r = RESPONSE_NO
    if len(toinstall):
        import string
        plist = string.join(toinstall, '\n')
	r = generic_longinfo_dialog(_("Shall the following packages, "
                                      "which are needed on your system, "
                                      "be installed?"),
                                    plist, dialog_type="question")
        return r
    return r

def request_rpms(pkgs = []):
    toinstall = rpms_notinstalled(pkgs)

    if len(toinstall):
        import string
        plist = string.join(toinstall, '\n')
        #print "toinstall %s" % str(toinstall)
        #print "plist %s" % str(plist)
	r = generic_longinfo_dialog(_("You have to install the following packages, "
                                      "which are needed on your system!"),
                                    plist, dialog_type="info")
        return 1
    return 0



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

def getHardwareType(devname):
    return getDeviceType(devname)

def getDeviceType(devname):
    type = _('Unknown')
    if not devname or devname == "":
        return type
    
    for i in deviceTypeDict.keys():
        if re.search(i, devname):
            type = deviceTypeDict[i]

    if type == ETHERNET:
        try:
	    # test for wireless
	    info = ethtool.get_iwconfig(devname)
	    type = WIRELESS
        except IOError:
	    pass

    return type

def getNewDialupDevice(devicelist, dev):
    dlist = []
    count = 0
    device = None

    for i in devicelist:
	if dev.Device != i.Device:
	    dlist.append(i.Device)
	    if i.Type == ISDN and i.Dialup.EncapMode == 'syncppp' and i.Dialup.ChannelBundling:
	        dlist.append(i.Dialup.SlaveDevice)
	else:
	    if i.Type == ISDN and i.Dialup.EncapMode == 'syncppp' and i.Dialup.ChannelBundling:
	        dlist.append(i.Device)

    if dev.Type == ISDN:
        if dev.Dialup.EncapMode == 'syncppp':
	    device = 'ippp'
	else:
	    device = 'isdn'
    else:
        device = 'ppp'

    while 1:
        if device+str(count) in dlist:
	    count = count + 1
	else:
	    return device+str(count)
	

ModemList = None
def getModemList():
    global ModemList
    if ModemList:
	    return ModemList[:]
    
    import kudzu
    res = kudzu.probe(kudzu.CLASS_MODEM, kudzu.BUS_UNSPEC, kudzu.PROBE_ALL)
    ModemList = []
    if res != []:
        for v in res:
	    dev = str(v[0])
	    if dev != 'None':
	        ModemList.append('/dev/' + dev)
    return ModemList[:]

# Some failsafe return codes (same as in gtk)
RESPONSE_NONE = -1
RESPONSE_REJECT = -2
RESPONSE_ACCEPT = -3
RESPONSE_DELETE_EVENT = -4
RESPONSE_OK = -5
RESPONSE_CANCEL = -6
RESPONSE_CLOSE = -7
RESPONSE_YES = -8
RESPONSE_NO = -9
RESPONSE_APPLY = -10
RESPONSE_HELP = -11

generic_error_dialog_func = None
def generic_error_dialog (message, parent_dialog = None, dialog_type="warning",
			  widget=None, page=0, broken_widget=None):
	global generic_error_dialog_func
	if generic_error_dialog_func:
		return generic_error_dialog_func(message, parent_dialog,
						 dialog_type, widget,
						 page, broken_widget)
        else:
            print message
	return 0

generic_info_dialog_func = None
def generic_info_dialog (message, parent_dialog = None, dialog_type="info",
			  widget=None, page=0, broken_widget=None):
	global generic_info_dialog_func
	if generic_info_dialog_func:
		return generic_info_dialog_func(message, parent_dialog,
						 dialog_type, widget,
						 page, broken_widget)
        else:
            print message
	return 0

generic_longinfo_dialog_func = None
def generic_longinfo_dialog (message, long_message,
			     parent_dialog = None, dialog_type="info",
			     widget=None, page=0, broken_widget=None):
	global generic_longinfo_dialog_func
	if generic_longinfo_dialog_func:
		return generic_longinfo_dialog_func(message, long_message,
						    parent_dialog,
						    dialog_type, widget,
						    page, broken_widget)
        else:
            print message
	return 0

generic_yesnocancel_dialog_func = None
def generic_yesnocancel_dialog (message, parent_dialog = None,
                                dialog_type="question",
                                widget=None, page=0, broken_widget=None):
	global generic_yesnocancel_dialog_func
	if generic_yesnocancel_dialog_func:
		return generic_yesnocancel_dialog_func(message, parent_dialog,
						       dialog_type, widget,
						       page, broken_widget)
        else:
            print message
	return 0

generic_yesno_dialog_func = None
def generic_yesno_dialog (message, parent_dialog = None,
			  dialog_type="question",
			  widget=None, page=0, broken_widget=None):
	global generic_yesno_dialog_func
	if generic_yesno_dialog_func:
		return generic_yesno_dialog_func(message, parent_dialog,
						 dialog_type, widget,
						 page, broken_widget)
        else:
            print message
	return 0

def set_generic_error_dialog_func(func):
	global generic_error_dialog_func
	generic_error_dialog_func = func

def set_generic_info_dialog_func(func):
	global generic_info_dialog_func
	generic_info_dialog_func = func
	
def set_generic_longinfo_dialog_func(func):
	global generic_longinfo_dialog_func
	generic_longinfo_dialog_func = func
	
def set_generic_yesnocancel_dialog_func(func):
	global generic_yesnocancel_dialog_func
	generic_yesnocancel_dialog_func = func
	
def set_generic_yesno_dialog_func(func):
	global generic_yesno_dialog_func
	generic_yesno_dialog_func = func

def unlink(file):
	if not os.path.isfile(file):
		#print "file '%s' is not a file!" % file
		return
	try:
		os.unlink(file)
                #print "Removed %s" % file
	except OSError, errstr:
                generic_error_dialog (_("Error removing\n%s:\n%s!") \
				      % (file, str(errstr)))

def link(src, dst):
	if not os.path.isfile(src):
		return
	try:
		os.link(src, dst)
	except OSError, errstr:
		generic_error_dialog (_("Error linking %s\nto\n%s:\n%s!") 
				      % (src, dst, str(errstr)))
	
def copy(src, dst):
	if not os.path.isfile(src):
		return
	try:
		shutil.copy(src, dst)
                shutil.copymode(src, dst)
	except (IOError, OSError), errstr:
		generic_error_dialog (_("Error copying \n%s\nto %s:\n%s!") 
				      % (src, dst, str(errstr)))
	
def symlink(src, dst):
	if not os.path.isfile(src):
		return
	try:
		os.symlink(src, dst)
	except OSError, errstr:
		generic_error_dialog (_("Error linking \n%s\nto %s:\n%s!") 
				      % (src, dst, str(errstr)))

def rename(src, dst):
	if not os.path.isfile(src) and not os.path.isdir(src):
		return
        try:
		os.rename(src, dst)
	except (IOError, OSError, EnvironmentError), errstr:
		generic_error_dialog (_("Error renaming \n%s\nto %s:\n%s!") \
				      % (src, dst, str(errstr)))
	
def get_filepath(file):
	fn = file
	if not os.path.exists(fn):
		fn = NETCONFDIR + file
	else: return fn
	
	if not os.path.exists(fn):
		return None
	else: return fn
	
	
