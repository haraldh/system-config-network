from DeviceList import *
from NC_functions import *
from os.path import *
from commands import *
import HardwareList
import string

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
                'Domain' : 'DOMAIN',
                'BootProto' : 'BOOTPROTO',
                'Type' : 'TYPE',
                }

    boolkeydict = { 'OnBoot' : 'ONBOOT',
                    'AllowUser' : 'USERCTL',
                    'AutoDNS' : 'RESOLV_MODS',
                    }
        
    def __init__(self, list = None, parent = None):
        Device_base.__init__(self, list, parent)        

    def createDialup(self):
        if self.Type:
            if self.Type == "Modem":
                if (self.Dialup == None) \
                   or not isinstance(self.Dialup, NCDialup.ModemDialup):
                    self.Dialup = NCDialup.ModemDialup(None, self)
                return self.Dialup
            elif self.Type == "Isdn":
                if (self.Dialup == None) \
                   or not isinstance(self.Dialup, NCDialup.IsdnDialup):
                    self.Dialup = NCDialup.IsdnDialup(None, self)
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

        aliaspos = string.find(self.Device, ':')
        if aliaspos != -1:
            self.Alias = int(self.Device[aliaspos+1:])
            self.Device = self.Device[:aliaspos]

        if not self.Type or self.Type == "" or self.Type == "Unknown":
            hwlist = HardwareList.getHardwareList()
            for hw in hwlist:
                if hw.Name == self.Device:
                    self.Type = hw.Type
                    
        if (not self.Type or self.Type == "" or self.Type == "Unknown" ) \
           and self.Device:            
            self.Type = getDeviceType(self.Device)

        #print "Creating Dialup"
        dialup = self.createDialup()
        if dialup:
            #print "Loading Dialup"
            dialup.load(conf)

        self.commit()
                
    def save(self):
        self.commit()

        conf = ConfDevice(self.DeviceId)

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        if self.Alias != None:
            conf['DEVICE'] = str(self.Device) + ':' + str(self.Alias)

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = 'yes'
            else:
                conf[confkey] = 'no'
                    
        if self.Dialup:
            self.Dialup.save(conf)
            
        conf.write()
