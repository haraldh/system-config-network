from DeviceList import *
from NC_functions import *
from os.path import *
from commands import *

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
import Conf

class ConfDevice(Conf.ConfShellVar):
    def __init__(self, name):
        Conf.ConfShellVar.__init__(self, SYSCONFDEVICEDIR + 'ifcfg-' + name)
            
class Device(Device_base):
    keydict = { 'Device' : 'DEVICE',
                'Name' : 'NAME',
                'OnBoot' : 'ONBOOT',
                'IP' : 'IPADDR',
                'Netmask' : 'NETMASK',
                'Gateway' : 'GATEWAY',
                'Hostname' : 'DEVHOSTNAME',
                'BootProto' : 'BOOTPROTO',
                }

    boolkeydict = { 'OnBoot' : 'ONBOOT',
                    'AllowUser' : 'USERCTL',
                    'AutoDNS' : 'RESOLV_MODS',
                    }
        
    def __init__(self, list = None, parent = None):
        Device_base.__init__(self, list, parent)        

    def createDialup(self):
        if self.Device:
            type = getDeviceType(self.DeviceId)
            if type == "Modem":
                if (self.Dialup == None) \
                   or not isinstance(self.Dialup, NCDialup.ModemDialup):
                    self.Dialup = NCDialup.ModemDialup(None, self)
                return self.Dialup
            else:
                return None
                    
        else:
            raise TypeError, "Device type not specified"
        
    def load(self, name):
        
        conf = ConfDevice(name)

        self.DeviceId = name
        
        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                self.__dict__[selfkey] = conf[confkey]

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'yes':
                    self.__dict__[selfkey] = true
                else:
                    self.__dict__[selfkey] = false            
            else:
                self.__dict__[selfkey] = false            

        if not self.Gateway:
            try:
                cfg = Conf.ConfShellVar(SYSCONFNETWORK)
                if cfg.has_key('GATEWAY'):
                    gw = cfg['GATEWAY']
                    
                    if gw and self.Netmask:                    
                        network = getoutput('ipcalc --network ' + self.IP \
                                            + ' ' + self.Netmask + \
                                            ' 2>/dev/null')
                        
                        out = getoutput('ipcalc --network ' + gw + ' ' \
                                        + self.Netmask + ' 2>/dev/null')
                        
                        if out == network:
                            self.Gateway = gw
                            
            except (OSError, IOError), msg:
                pass

                    
        #print "Creating Dialup"
        dialup = self.createDialup()
        if dialup:
            #print "Loading Dialup"
            dialup.load(conf)
                
    def save(self):
        conf = ConfDevice(self.DeviceId)

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = 'yes'
            else:
                conf[confkey] = 'no'
                    
        if self.Dialup:
            self.Dialup.save(conf)
            
        conf.write()
