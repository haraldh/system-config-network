## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
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
from rhpl import Conf
from rhpl import ConfSMB
import rhpl.log


import UserList

import string

true = (1==1)
false = not true

PROGNAME = "system-config-network"

import locale
from rhpl.translate import _, N_, textdomain_codeset
locale.setlocale(locale.LC_ALL, "")
textdomain_codeset(PROGNAME, locale.nl_langinfo(locale.CODESET))
import __builtin__
__builtin__.__dict__['_'] = _

_kernel_version = None
def kernel_version():
    global _kernel_version
    if not _kernel_version:
        (sysname, nodename, release, version, machine) = os.uname()
        if release.find("-") != -1:
            (ver, rel) = release.split("-", 1)
        else:
            ver = release
        _kernel_version = string.split(ver, ".", 4)        
    return _kernel_version

def cmp_kernel_version(v1, v2):
    for i in (1, 2, 3):
        if v1[i] != v2[i]:
            try:
                return int(v1[i]) - int(v2[i])
            except:
                if (v1[i] > v2[i]):
                    return 1
                else:
                    return -1
    return 0
    

NETCONFDIR = '/usr/share/system-config-network/'
OLDSYSCONFDEVICEDIR = '/etc/sysconfig/network-scripts/'
SYSCONFNETWORKING = '/etc/sysconfig/networking/'
SYSCONFDEVICEDIR = SYSCONFNETWORKING + 'devices/'
SYSCONFPROFILEDIR = SYSCONFNETWORKING + 'profiles/'
SYSCONFNETWORK = '/etc/sysconfig/network'
WVDIALCONF = '/etc/wvdial.conf'
HOSTSCONF = '/etc/hosts'
RESOLVCONF = '/etc/resolv.conf'
CIPEDIR = "/etc/cipe"
PPPDIR = "/etc/ppp"

if cmp_kernel_version([2,5,0], kernel_version()) < 0:
    MODULESCONF='/etc/modprobe.conf'
    DOCIPE=0
else:
    MODULESCONF='/etc/modules.conf'
    DOCIPE=1
    
HWCONF='/etc/sysconfig/hwconf'
ISDNCARDCONF='/etc/sysconfig/isdncard'
PAPFILE = "/etc/ppp/pap-secrets"
CHAPFILE = "/etc/ppp/chap-secrets"

import netconfpkg
netconfpkg.ROOT = "/"

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
IPSEC = 'IPSEC'
QETH = 'QETH'
HSI = 'HSI'

deviceTypes = [ ETHERNET, MODEM, ISDN, LO, DSL, CIPE, WIRELESS, TOKENRING, CTC, IUCV, QETH, HSI ]

modemDeviceList = [ '/dev/modem',
                    '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3',
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
		   '^hsi[0-9]*(:[0-9]+)?$' : HSI,
		   '^iucv[0-9]*(:[0-9]+)?$' : IUCV,
		   '^wlan[0-9]*(:[0-9]+)?$' : WIRELESS,                   
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

_verbose = 0

def setVerboseLevel(l):
    global _verbose
    #print "Set verbose %d" % l
    _verbose = l

def getVerboseLevel():
    global _verbose
    #print "verbose == %d" % _verbose
    return _verbose

_debug = 0

def setDebugLevel(l):
    global _debug
    #print "Set debug %d" % l
    _debug = l

def getDebugLevel():
    global _debug
    #print "debug == %d" % _debug
    return _debug

class TestError(Exception):
    def __init__(self, args=None):
        Exception.__init__(self, args)
        #self.args = args

def gen_hexkey(len = 16):
    import struct
    key = ""
    f = file("/dev/random", "rb")
    chars = struct.unpack("%dB" % len, f.read(len))
    for i in chars:        
        key = key + "%02x" % i
    f.close()
    return key

def rpms_notinstalled(namelist):
    try:
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
                #print n[rpm.RPMTAG_NAME]
                if n[rpm.RPMTAG_NAME] == name:
                    toinstall.remove(name)
                    break

        del (ts)
        return toinstall
    except:
        return []
    
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
	r = generic_longinfo_dialog(_("You have to install the following packages, "
                                      "which are needed on your system!"),
                                    plist, dialog_type="info")
        return 1
    return 0

def netmask_to_bits(netmask):
    import string
    vals = string.split(netmask, ".")
    if len(vals) == 4:
        netmask = 0
        for val in vals:
            netmask *= 256
            try: netmask += long(val)
            except: pass
    else:
        return 0
    
    bits = 0
    while netmask:
        if netmask & 1: bits += 1
        netmask = netmask >> 1

    return bits

def bits_to_netmask(bits):
    try:
        bits = int(bits)
    except:
        return ""
    
    rem = 32 - bits
    netmask = long(0)

    while bits:
        netmask = netmask << 1
        netmask = netmask | 1
        bits -= 1
        
    while rem:
        netmask = netmask << 1
        rem -= 1
    
    netstr = str(netmask >> 24) + "." + \
             str(netmask >> 16 & 255) + "." + \
             str(netmask >> 8 & 255) + "." + \
             str(netmask & 255)

    return netstr

DVpapconf = None
def getPAPConf():
    global DVpapconf
    if DVpapconf == None or DVpapconf.filename != netconfpkg.ROOT + PAPFILE:
        DVpapconf = ConfPAP.ConfPAP(netconfpkg.ROOT + PAPFILE)
    return DVpapconf

DVchapconf = None
def getCHAPConf():
    global DVchapconf
    if DVchapconf == None or DVchapconf.filename != netconfpkg.ROOT + CHAPFILE:
        DVchapconf = ConfPAP.ConfPAP(netconfpkg.ROOT + CHAPFILE)
    return DVchapconf


def create_combo(hardwarelist, devname, type, default_devices):
    hwdesc = default_devices
    hwcurr = None

    for hw in hardwarelist:
        if hw.Type == type:
            desc = str(hw.Name)
            if hw.Description:
                desc += ' (' + hw.Description + ')'
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

def create_generic_combo(hardwarelist, devname, type = ETHERNET, new = None):
    devbase = re.sub('[0-9]*(:[0-9]+)?$', '', devname)
    hwdesc = []
    for i in xrange(0, 9):
        hwdesc.append(devbase + str(i))

    if not new:
        return create_combo(hardwarelist, devname, type,
                            default_devices = hwdesc)
    else:
        return (None, hwdesc)
    

def create_ethernet_combo(hardwarelist, devname, type = ETHERNET):
    hwdesc = [ 'eth0', 'eth1', 'eth2',
               'eth3', 'eth4', 'eth5',
               'eth6', 'eth7', 'eth8'
               ]

    return create_combo(hardwarelist, devname, type,
                        default_devices = hwdesc)

def create_tokenring_combo(hardwarelist, devname):
    hwdesc = [ 'tr0', 'tr1', 'tr2',
               'tr3', 'tr4', 'tr5',
               'tr6', 'tr7', 'tr8'
               ]
    return create_combo(hardwarelist, devname, type = TOKENRING,
                        default_devices = hwdesc)

def ishardlink(file):
    if os.path.isfile(file):
        return os.stat(file)[3] > 1
    else:
        return None

def issamefile(file1, file2):
    try:
        s1 = os.stat(file1)
        s2 = os.stat(file2)
    except:
        return false
    return os.path.samestat(s1, s2)

def getHardwareType(devname):
    if devname in deviceTypes:
        return devname
    return getDeviceType(devname)

def getDeviceType(devname):    
    if devname in deviceTypes:
        return devname

    UNKNOWN = _('Unknown')
    
    type = UNKNOWN
    if not devname or devname == "":
        return type
    
    for i in deviceTypeDict.keys():
        if re.search(i, devname):
            type = deviceTypeDict[i]

    if type == UNKNOWN:
        try:
            # if still unknown, try to get a MAC address
            hwaddr = ethtool.get_hwaddr(devname)
            if hwaddr:
                type = ETHERNET
        except:
            pass        

    if type == ETHERNET:
        try:
	    # test for wireless
	    info = ethtool.get_iwconfig(devname)
	    type = WIRELESS
        except IOError:
	    pass
        
    return type

def getNickName(devicelist, dev):
    nickname = []
    for d in devicelist:
        if d.Device == dev:
            nickname.append(d.DeviceId)
    return nickname

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
	    dev = str(v.device)
	    if dev and dev != 'None':
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
		return generic_error_dialog_func("%s:\n\n%s" % (PROGNAME,
                                                                message),
                                                 parent_dialog,
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
		return generic_info_dialog_func("%s:\n\n%s" % (PROGNAME,
                                                               message),
                                                parent_dialog,
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
		return generic_longinfo_dialog_func("%s:\n\n%s" % (PROGNAME,
                                                                   message),
                                                    long_message,
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
		return generic_yesnocancel_dialog_func("%s:\n\n%s" % (PROGNAME,
                                                                      message),
                                                       parent_dialog,
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
		return generic_yesno_dialog_func("%s:\n\n%s" % (PROGNAME,
                                                                message),
                                                 parent_dialog,
						 dialog_type, widget,
						 page, broken_widget)
        else:
            print message
	return 0

generic_run_dialog_func = None
def generic_run_dialog (command, argv, searchPath = 0,
                        root = '/', stdin = 0,
                        catchfd = 1, closefd = -1, title = None,
                        label = None, errlabel = None, dialog = None):
        import select
        global generic_run_dialog_func
	if generic_run_dialog_func:
		return generic_run_dialog_func(command, argv, searchPath,
                                               root, stdin, catchfd,
                                               title = "%s:\n\n%s" % (PROGNAME,
                                                                      title),
                                               label = label,
                                               errlabel = errlabel,
                                               dialog = dialog)
        else:
            if not os.access (root + command, os.X_OK):
                raise RuntimeError, command + " can not be run"

            print title
            print label

            log.log(1, "Running %s %s" % (command, string.join(argv)))
            (read, write) = os.pipe()

            childpid = os.fork()
            if (not childpid):
                if (root and root != '/'): os.chroot (root)
                if isinstance(catchfd, tuple):
                    for fd in catchfd:
                        os.dup2(write, fd)
                else:
                    os.dup2(write, catchfd)
                os.close(write)
                os.close(read)

                if closefd != -1:
                    os.close(closefd)

                if stdin:
                    os.dup2(stdin, 0)
                    os.close(stdin)

                if (searchPath):                    
                    os.execvp(command, argv)
                else:
                    os.execv(command, argv)

                sys.exit(1)
            try:
                os.close(write)

                rc = ""
                s = "1"
                while (s):
                    try:
                        (fdin, fdout, fderr) = select.select([read], [], [], 0.1)
                    except:
                        fdin = []
                        pass

                    if len(fdin):
                        s = os.read(read, 100)
                        sys.stdout.write(s)
                        rc = rc + s

            except Exception, e:
                try:
                    os.kill(childpid, 15)
                except:
                    pass
                raise e

            os.close(read)

            try:
                (pid, status) = os.waitpid(childpid, 0)
            except OSError, (errno, msg):
                #print __name__, "waitpid:", msg
                pass

            if os.WIFEXITED(status) and (os.WEXITSTATUS(status) == 0):
                status = os.WEXITSTATUS(status)
            else:
                status = -1

            return (status, rc)

generic_run_func = None
def generic_run (command, argv, searchPath = 0,
                 root = '/', stdin = 0,
                 catchfd = 1, closefd = -1):
        import select
        global generic_run_func
	if generic_run_func:
		return generic_run_func(command, argv, searchPath,
                                               root, stdin, catchfd)
        else:
            if not os.access (root + command, os.X_OK):
                raise RuntimeError, command + " can not be run"

            log.log(1, "Running %s %s" % (command, string.join(argv)))
            (read, write) = os.pipe()

            childpid = os.fork()
            if (not childpid):
                if (root and root != '/'): os.chroot (root)
                if isinstance(catchfd, tuple):
                    for fd in catchfd:
                        os.dup2(write, fd)
                else:
                    os.dup2(write, catchfd)
                os.close(write)
                os.close(read)

                if closefd != -1:
                    os.close(closefd)

                if stdin:
                    os.dup2(stdin, 0)
                    os.close(stdin)

                if (searchPath):                    
                    os.execvp(command, argv)
                else:
                    os.execv(command, argv)

                sys.exit(1)
            try:
                os.close(write)

                rc = ""
                s = "1"
                while (s):
                    try:
                        (fdin, fdout, fderr) = select.select([read],
                                                             [], [], 0.1)
                    except:
                        fdin = []
                        pass

                    if len(fdin):
                        s = os.read(read, 100)
                        sys.stdout.write(s)
                        rc = rc + s

            except Exception, e:
                try:
                    os.kill(childpid, 15)
                except:
                    pass
                raise e

            os.close(read)

            try:
                (pid, status) = os.waitpid(childpid, 0)
            except OSError, (errno, msg):
                #print __name__, "waitpid:", msg
                pass

            if os.WIFEXITED(status) and (os.WEXITSTATUS(status) == 0):
                status = os.WEXITSTATUS(status)
            else:
                status = -1

            return (status, rc)

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

def set_generic_run_dialog_func(func):
	global generic_run_dialog_func
	generic_run_dialog_func = func

def set_generic_run_func(func):
	global generic_run_func
	generic_run_func = func
   

def unlink(file):
	if not (os.path.isfile(file) or os.path.islink(file)):
		#print "file '%s' is not a file!" % file
		return
	try:
		os.unlink(file)
                log.log(2, "rm %s" % file)
	except OSError, errstr:
                generic_error_dialog (_("Error removing\n%s:\n%s!") \
				      % (file, str(errstr)))

def rmdir(file):
    if not os.path.isdir(file):
        #print "file '%s' is not a file!" % file
        return
    try:
        os.rmdir(file)
        log.log(2, "rmdir %s" % file)
    except OSError, errstr:
        generic_error_dialog (_("Error removing\n%s:\n%s!") \
                              % (file, str(errstr)))
        
def link(src, dst):
	if not os.path.isfile(src):
		return
	try:
		os.link(src, dst)
                log.log(2, "ln %s %s" % (src, dst))
	except:
            symlink(src, dst)
            
def copy(src, dst):
	if not os.path.isfile(src):
		return
	try:
		shutil.copy(src, dst)
                shutil.copymode(src, dst)
                log.log(2, "cp %s %s" % (src, dst))
	except (IOError, OSError), errstr:
		generic_error_dialog (_("Error copying \n%s\nto %s:\n%s!") 
				      % (src, dst, str(errstr)))
	
def symlink(src, dst):
	if not os.path.isfile(src):
		return
	try:
		os.symlink(src, dst)
                log.log(2, "ln -s %s %s" % (src, dst))
	except OSError, errstr:
		generic_error_dialog (_("Error linking \n%s\nto %s:\n%s!") 
				      % (src, dst, str(errstr)))

def rename(src, dst):
	if not os.path.isfile(src) and not os.path.isdir(src):
		return
        try:
		os.rename(src, dst)
                log.log(2, "mv %s %s" % (src, dst))
	except (IOError, OSError, EnvironmentError), errstr:
		generic_error_dialog (_("Error renaming \n%s\nto %s:\n%s!") \
				      % (src, dst, str(errstr)))

def mkdir(path):
    try:
        os.mkdir(path)
        log.log(2, "mkdir %s" % path)
    except (IOError, OSError), errstr :
        generic_error_dialog (_("Error creating directory!\n%s") \
                              % (str(errstr)))

def get_filepath(file):
	fn = file
	if not os.path.exists(fn):
		fn = NETCONFDIR + file
	else: return fn
	
	if not os.path.exists(fn):
		return None
	else: return fn

class ConfDevices(UserList.UserList):
    def __init__(self, confdir = None):
        UserList.UserList.__init__(self)
        if confdir == None:
            confdir = netconfpkg.ROOT + SYSCONFDEVICEDIR
        confdir += '/'
        try:
            dir = os.listdir(confdir)            
        except OSError, msg:
            pass
        else:
            for entry in dir:
                if (len(entry) > 6) and \
                   entry[:6] == 'ifcfg-' and \
                   os.path.isfile(confdir + entry) and \
                   (confdir + entry)[-1] != "~" and \
                   string.find(entry, '.rpmsave') == -1 and \
                   string.find(entry, '.rpmnew') == -1 and \
                   os.access(confdir + entry, os.R_OK):
                    self.append(entry[6:])

def testFilename(filename):
    if not len(filename):
        return false
    
    if (not os.access(filename, os.R_OK)) or \
           (not os.path.isfile(filename)) or \
           (os.path.islink(filename)):
        return false

    if filename[-1] == "~":
        return false

    if len(filename) > 7 and filename[:7] == '.rpmnew':
        return false

    if len(filename) > 8 and filename[:8] == '.rpmsave':
        return false

    if len(filename) > 8 and filename[:8] == '.rpmorig':
        return false

    return true

def setRoot(root):
    netconfpkg.ROOT = root

def getRoot():
    return netconfpkg.ROOT

def prepareRoot(root):
    setRoot(root)
    
    for dir in "/etc", "/etc/sysconfig", \
        SYSCONFNETWORKING, \
        OLDSYSCONFDEVICEDIR, \
        SYSCONFDEVICEDIR, \
        SYSCONFPROFILEDIR, \
        CIPEDIR, PPPDIR:
        if not os.path.isdir(root + dir):
            mkdir(root + dir)


class ConfKeys(Conf.ConfShellVar):
    def __init__(self, name):
        Conf.ConfShellVar.__init__(self, netconfpkg.ROOT + SYSCONFDEVICEDIR + 'keys-' + name)
        self.chmod(0600)


__updatedNetworkScripts = 0

def updateNetworkScripts(force = false):
    global __updatedNetworkScripts
    
    if __updatedNetworkScripts and (not force):
        return

    if not os.access(getRoot(), os.W_OK):
        return
        
    prepareRoot(getRoot())

    firsttime = 0
    
    if not os.path.isdir(netconfpkg.ROOT + SYSCONFPROFILEDIR+'/default/'):
        firsttime = 1
        mkdir(netconfpkg.ROOT + SYSCONFPROFILEDIR+'/default')

    curr_prof = 'default'
    if not firsttime:
        nwconf = Conf.ConfShellVar(netconfpkg.ROOT + SYSCONFNETWORK)
        if nwconf.has_key('CURRENT_PROFILE'):
            curr_prof = nwconf['CURRENT_PROFILE']

    devlist = ConfDevices(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR)

    for dev in devlist:
        if dev == 'lo':           
            continue

        ocfile = netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+'/ifcfg-'+ dev
        dfile = netconfpkg.ROOT + SYSCONFDEVICEDIR+'/ifcfg-'+dev

        if issamefile(ocfile, dfile):
            continue
        
        unlink(netconfpkg.ROOT + SYSCONFDEVICEDIR+'/ifcfg-'+dev)
        link(ocfile, dfile)

        log.log(1, _("Linking %s to devices and putting "
                     "it in profile %s.") % (dev, curr_prof))

        pfile = netconfpkg.ROOT + SYSCONFPROFILEDIR+'/' + curr_prof + '/ifcfg-'+dev

        unlink(pfile)
        link(dfile, pfile)

        for (file, cfile) in { RESOLVCONF : '/resolv.conf', HOSTSCONF : '/hosts' }.items():
            hostfile = netconfpkg.ROOT + file
            conffile = netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + \
                       curr_prof + cfile
            if not os.path.isfile(hostfile) or not issamefile(hostfile, conffile):
                unlink(conffile)
                link(hostfile, conffile)

    __updatedNetworkScripts = 1

#
# log.py - debugging log service
#
# Alexander Larsson <alexl@redhat.com>
# Matt Wilson <msw@redhat.com>
#
# Copyright 2002 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import sys
import syslog

class LogFile:
    def __init__ (self, level = 0, filename = None):
        if filename == None:
            import syslog
            self.syslog = syslog.openlog(PROGNAME, syslog.LOG_PID)
                                        
            self.handler = self.syslog_handler
            self.logFile = sys.stderr
        else:
            self.handler = self.file_handler
            self.open(filename)
            
        self.level = level

    def close (self):
        try:
            self.logFile.close ()
        except:
            pass        

    def open (self, file = None):
	if type(file) == type("hello"):
            try:
                self.logFile = open(file, "w")
            except:
                self.logFile = sys.stderr
	elif file:
	    self.logFile = file
	else:
            self.logFile = sys.stderr
        
    def getFile (self):
        return self.logFile.fileno ()

    def __call__(self, format, *args):
	self.handler (format % args)
        
    def file_handler (self, string, level = 0):
        import time
        self.logFile.write ("[%d] %s: %s\n" % (level, time.ctime(), string))

    def syslog_handler (self, string, level = syslog.LOG_INFO):
        import syslog
	syslog.syslog(level, string)

    def set_loglevel(self, level):
        self.level = level

    def log(self, level, message):
        if self.level >= level:
            self.handler(message, level = level)

    def ladd(self, level, file, message):
        if self.level >= level:
            self.handler("++ %s \t%s" % (file, message))

    def ldel(self, level, file, message):
        if self.level >= level:
            self.handler("-- %s \t%s" % (file, message))

    def lch(self, level, file, message):
        if self.level >= level:
            self.handler("-+ %s \t%s" % (file, message))


log = LogFile()
						
rhpl.log = log

            
__author__ = "Harald Hoyer <harald@redhat.com>"
