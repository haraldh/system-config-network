import sys
import ConfSMB

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

import Conf

from DeviceList import *
from NC_functions import *
        
class Dialup(Dialup_base):
    def __init__(self, list = None, parent = None):
        Dialup_base.__init__(self, list, parent)        

class IsdnDialup(Dialup):                        

    boolkeydict = { 'Secure' : 'SECURE',
                    'ChannelBundling' : 'BUNDLING',
                    'DefRoute' : 'DELDEFAULTROUTE',
                    }
    
    intkeydict = {'MSN' : 'MSN',
                  'DialMax' : 'DIALMAX',
                  'HangupTimeout' : 'HUPTIMEOUT',
                  }
    
    keydict = { 'ProviderName' : 'PROVIDER',
                'Login' : 'USER',
                'Password' : 'PASSWORD',
                'EncapMode' : 'ENCAP',
                'DialMode' : 'DIALMODE',                 
                'Prefix' : 'PREFIX',
                'Areacode' : 'AREACODE',
                'Regioncode' : 'REGIONCODE',
                'PhoneOut' : 'PHONE_OUT',
                'PrimaryDNS' : 'DNS1',
                'SecondaryDNS' : 'DNS2',
                'Layer2' : 'LAYER',
                'ChargeHup' : 'CHARGEHUP',
                'ChargeInt' : 'CHARGEINT',
                'Authentication' : 'AUTH',
                'Ihup' : 'IHUP',
                'SlaveDevice' : 'SLAVE_DEVICE',
                'Layer2' : 'L2_PROT',
                }
    
    def __init__(self, list = None, parent = None):
        Dialup.__init__(self, list, parent)        

    def load(self, parentConf):
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                self.__dict__[selfkey] = conf[confkey]
                #print "self." + selfkey + " = " + conf[confkey]

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if conf.has_key(confkey) and len(conf[confkey]):
                self.__dict__[selfkey] = int(conf[confkey])
                #print "self." + selfkey + " = " + conf[confkey]

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'on':
                    self.__dict__[selfkey] = true
                else:
                    self.__dict__[selfkey] = false            
            else:
                self.__dict__[selfkey] = false            

        if conf.has_key('DELDEFAULTROUTE'):
            if conf['DELDEFAULTROUTE'] == 'enabled':
                self.DefRoute = true
            else:
                self.DefRoute = false

        parent = self.getParent()

        if parent:
            if conf.has_key('LOCAL_IP'):
                parent.IP = conf['LOCAL_IP']
            if conf.has_key('REMOTE_IP'):
                parent.Gateway = conf['REMOTE_IP']
            if conf.has_key('BOOT'):
                if conf['BOOT'] == 'on':
                    parent.OnBoot = true
                else:
                    parent.OnBoot = false

        if not self.PPPOptions:
            self.createPPPOptions()
        
        compression = self.createCompression()
        compression.load(conf)
        
        if conf['VJ'] == 'on' or conf['VJ'] == 'yes':
            compression.VJTcpIp = true
        else:
            compression.VJTcpIp = false
        if conf['VJCCOMP'] == 'on' or conf['VJCCOMP'] == 'yes':
            compression.VJID = true
        else:
            compression.VJID = false
        if conf['AC'] == 'on' or conf['AC'] == 'yes':
            compression.AdressControl = true
        else:
            compression.AdressControl = false
        if conf['PC'] == 'on' or conf['PC'] == 'yes':
            compression.ProtoField = true
        else:
            compression.ProtoField = false
        if conf['BSDCOMP'] == 'on' or conf['BSDCOMP'] == 'yes':
            compression.BSD = true
        else:
            compression.BSD = false
        if conf['CCP'] == 'on' or conf['CCP'] == 'yes':
            compression.CCP = true
        else:
            compression.CCP = false

        if conf.has_key('CALLBACK'):
            if conf['CALLBACK'] == 'on':
                callback = self.createCallback()
                callback.load(conf)
                callback.Number = conf['PHONE_IN']
                callback.Delay = string.atoi(conf['CBDELAY'])
                callback.Hup = conf['CBHUP']
                if conf['CBCP'] == 'on' or conf['CBCP'] == 'yes':
                    callback.CBCP = true
                else:
                    callback.CBCP = false
            else:
                self.delCallback()

        self.commit()

    def save(self, parentConf):
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = 'on'
            else:
                conf[confkey] = 'off'

        if self.DefRoute:
            conf['DELDEFAULTROUTE'] = 'enabled'
        else:
            conf['DELDEFAULTROUTE'] = 'disabled'

        parent = self.getParent()

        if conf.has_key('LOCAL_IP'):
            del conf['LOCAL_IP']
        if conf.has_key('REMOTE_IP'):
            del conf['REMOTE_IP']
        if conf.has_key('BOOT'):
            del conf['BOOT']

        if self.Compression:
            self.Compression.save(conf)
            
        if self.Callback:
            conf['CALLBACK'] == 'on'
            self.Callback.save(conf)
        else:
            conf['CALLBACK'] == 'off'

        conf.write()
        
    
class ModemDialup(Dialup):
    wvdict = { 'Login' : 'Username',
               'Password' : 'Password',
               'Prefix' : 'Dial Prefix',
               'Areacode' : 'Area Code',
               'PhoneNumber' : 'Phone',
               }                   
                        
    def __init__(self, list = None, parent = None):
        Dialup.__init__(self, list, parent)                

    def load(self, parentConf):
        parent = self.getParent()

        if parent:
            name = parent.DeviceId
            
        if parentConf.has_key('WVDIALSECT'):
            name = parentConf['WVDIALSECT']

        conf = ConfSMB.ConfSMB(filename = '/etc/wvdial.conf')
        
        sectname = 'Dialer ' + name

        for selfkey in self.wvdict.keys():
            confkey = self.wvdict[selfkey]
            value = None
            if conf.has_key(sectname) and conf[sectname].has_key(confkey):
                value = conf[sectname][confkey]
            elif conf.has_key('Dialer Defaults') \
               and conf['Dialer Defaults'].has_key(confkey):
                value = conf['Dialer Defaults'][confkey]
                
            if value:
                #print selfkey + " = " + value
                self.__dict__[selfkey] = value

        #
        # Read Modem Init strings
        #
        if not self.InitStrings: self.createInitStrings()
        for i in xrange(9) :
            confkey = 'Init'
            if i: confkey = confkey + str(i)                
            value = None
            
            if conf.has_key(sectname) and conf[sectname].has_key(confkey):
                value = conf[sectname][confkey]
            elif conf.has_key('Dialer Defaults') \
               and conf['Dialer Defaults'].has_key(confkey):
                value = conf['Dialer Defaults'][confkey]
                
            if value:
                #print confkey + " = " + value
                self.InitStrings[self.InitStrings.addInitString()] = value
                
        #
        # Workaround for backporting rp3-config stuff
        #
        if conf[sectname].has_key('Inherits'):
            if conf[sectname]['Inherits'] != 'Dialer Defaults' and \
               (len(conf[sectname]['Inherits']) > 5) and \
               conf[sectname]['Inherits'][:5] == 'Modem':
                if parent:
                    parent.Device = conf[sectname]['Inherits']
            elif conf[sectname]['Inherits'] == 'Dialer Defaults':
                #print "Has Defaults!"
                if conf.has_key('Dialer Defaults') and \
                   conf['Dialer Defaults'].has_key('Modem') and \
                   conf['Dialer Defaults'].has_key('Baud'):
                    modemdev = conf['Dialer Defaults']['Modem']
                    modembaud = conf['Dialer Defaults']['Baud']
                    #print "Modem = " + modemdev
                    #print "Baud = " + modembaud
                    for sect in conf.keys():
                        if (len(sect) <= 5) or (sect[:5] != 'Modem'):
                            #print "Skipping " + sect
                            continue
                        if conf[sect].has_key('Modem') and \
                           conf[sect].has_key('Baud') and \
                           conf[sect]['Modem'] == modemdev and \
                           conf[sect]['Baud'] == modembaud:
                            #print "Found " + sect
                            if parent:                                
                                parent.Device = sect
                            break
        
    def save(self, parentConf):
        parent = self.getParent()

        if parent:                                
            devname = parent.Device
            name = parent.DeviceId
        else:
            devname = '*'
            name = "Default"

        if not parentConf.has_key('WVDIALSECT'):
            # set WVDIALSECT in ifcfg-ppp[0-9] to DeviceId
            parentConf['WVDIALSECT'] = name
            sectname = 'Dialer ' + name
        else:
            # get section name
            sectname = parentConf['WVDIALSECT']

        # Correct PAPNAME in ifcfg-ppp[0-9]
        if self.Login:
            parentConf['PAPNAME'] = self.Login

        #
        # Write the wvdial section
        #
        conf = ConfSMB.ConfSMB(filename = '/etc/wvdial.conf')
        
        for selfkey in self.wvdict.keys():
            confkey = self.wvdict[selfkey]
            if self.__dict__[selfkey]:
                conf[sectname][confkey] = str(self.__dict__[selfkey])
            else:
                if conf[sectname].has_key(confkey):
                    del conf[sectname][confkey] 

        for i in xrange(min([len(self.InitStrings), 9])):
            confkey = 'Init'
            if i: confkey = confkey + str(i)                
            
            if self.InitStrings[i]:
                conf[sectname][confkey] = str(self.InitStrings[i])
            else:
                if conf[sectname].has_key(confkey):
                    del conf[sectname][confkey]

        conf[sectname]['Inherits'] = devname
                    
        conf.write()

        #
        # Now write the pap and chap-secrets
        #
        #print "device = " + name
        if not self.Login:
            return
        
        for secretfile in [ "/etc/ppp/pap-secrets", "/etc/ppp/chap-secrets" ]:
            conf = Conf.Conf(secretfile, '#', ' \t', ' \t')
            while conf.findnextcodeline():
                vars = conf.getfields()
                #print vars
                if vars and (len(vars) == 3) \
                   and ((vars[0] == self.Login) \
                        or (vars[0] == '"' + self.Login + '"')) \
                        and (vars[1] == name):
                    #print vars                    
                    #print conf.getline()
                    #print "login = " + self.Login + " " + self.Password
                    conf.setfields([self.Login, devname, self.Password])
                    #print conf.getline()                    
                    break
                    
                conf.nextline()
            conf.write()


if __name__ == '__main__':
    dev = Device()
    dev.load('ppp1')
    dev.Dialup.Password = "*********"
    dev.commit()
    dev.save()
