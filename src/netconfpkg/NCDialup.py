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

import sys
import ConfSMB

import string

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

import Conf
import gettext

import DeviceList
import NCCompression
import NCHardwareList
from NC_functions import *

##
## I18N
##
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
_=gettext.gettext

country_code = {
    _("None") : 0,
    _("Afghanistan") : 93,
    _("Albania") : 355,
    _("Algeria") : 213,
    _("American Samoa") : 684,
    _("Andorra") : 376,
    _("Argentina") : 54,
    _("Australia") : 61,
    _("Austria") : 43,
    _("Belgium") : 32,
    _("Bosnia and Herzegonia") : 387,
    _("Brazil") : 55,
    _("Britisch Virgin Islands") : 1, 
    _("Bulgaria") : 359,
    _("Canada") : 1,
    _("Central African Republic") : 236,
    _("Chile") : 56,
    _("China") : 86,
    _("Colombia") : 47,
    _("Croatia") : 385,
    _("Cuba") : 53,
    _("Czech Republic") : 420,
    _("Denmark") : 45,
    _("Finnland") : 358,
    _("France") : 33,
    _("Germany") : 49,
    _("Greece") : 30,
    _("Hong Kong") : 852,
    _("Hungary") : 36,
    _("Iceland") : 354,
    _("India") : 91,
    _("Indonesia") : 62,
    _("Ireland") : 353,
    _("Israel") : 972,
    _("Italy") : 39,
    _("Japan") : 81,
    _("Korea North") : 850,
    _("Korea Republic") : 82,
    _("Malaysia") : 60,
    _("Luxemburg") : 352,
    _("Mexico") : 52,
    _("Netherlands") : 31,
    _("New Zealand") : 64,
    _("Norway") : 47,
    _("Philippines") : 63,
    _("Romania") : 30,
    _("Singapore") : 65,
    _("Slovakia") : 421,
    _("Spain") : 34,
    _("Sweden") : 46,
    _("Switzerland") : 41,
    _("Taiwan") : 886,
    _("Thailand") : 66,
    _("Turkey") : 90,
    _("Ukraine") : 380,
    _("United Kingdom") : 44,
    _("United States of Amerika") : 1,
    _("Vietnam") : 84,
    _("Yugoslavia") : 381
    }

class Dialup(DeviceList.Dialup_base):
    def __init__(self, list = None, parent = None):
        DeviceList.Dialup_base.__init__(self, list, parent)        
        self.createCompression()
        
class DslDialup(Dialup):
    boolkeydict = { 'PeerDNS' : 'RESOLV_MODS',
                    'DefRoute' : 'DEFROUTE',
                    'SyncPPP' : 'SYNCHRONOUS',
                    }
    
    keydict = { 'ProviderName' : 'PROVIDER',
                'Login' : 'USER',
                'Password' : 'PASS',
                'PrimaryDNS' : 'DNS1',
                'SecondaryDNS' : 'DNS2',
                'EthDevice' : 'ETH',
                'SlaveDevice' : 'SLAVE_DEVICE',
                'ServiceName' : 'SERVICENAME',
                'AcName' : 'ACNAME',
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

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'yes':
                    self.__dict__[selfkey] = true
                else:
                    self.__dict__[selfkey] = false            
            else:
                self.__dict__[selfkey] = false            

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
                conf[confkey] = 'yes'
            else:
                conf[confkey] = 'no'

        if not conf.has_key('CONNECT_TIMEOUT'):
            conf['CONNECT_TIMEOUT'] = '60'

        if not conf.has_key('CONNECT_POLL'):
            conf['CONNECT_POLL'] = '6'

        if not conf.has_key('CLAMPMSS'):
            conf['CLAMPMSS'] = '1412'

        if not conf.has_key('LCP_INTERVAL'):
            conf['LCP_INTERVAL'] = '20'

        if not conf.has_key('LCP_FAILURE'):
            conf['LCP_FAILURE'] = '3'

        if not conf.has_key('PPPOE_TIMEOUT'):
            conf['PPPOE_TIMEOUT'] = '20'

        if not conf.has_key('PING'):
            conf['PING'] = '.'

        if not conf.has_key('FIREWALL'):
            conf['FIREWALL'] = 'NONE'

        if not conf.has_key('PIDFILE'):
            conf['PIDFILE'] = '/var/run/pppoe-adsl.pid'

        for i in conf.keys():
            if not conf[i]: del conf[i]

        if conf.has_key('RESOLV_MODS'):
            del conf['RESOLV_MODS']
        
        conf.write()


class IsdnDialup(Dialup):                        

    boolkeydict = { 'Secure' : 'SECURE',
                    'ChannelBundling' : 'BUNDLING',
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
                'PhoneNumber' : 'PHONE_OUT',
                'PrimaryDNS' : 'DNS1',
                'SecondaryDNS' : 'DNS2',
                'ChargeHup' : 'CHARGEHUP',
                'ChargeInt' : 'CHARGEINT',
                'Authentication' : 'AUTH',
                'Ihup' : 'IHUP',
                'SlaveDevice' : 'SLAVE_DEVICE',
                'Layer2' : 'L2_PROT',
                'Layer3' : 'L3_PROT',
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

#        if conf.has_key('DELDEFAULTROUTE'):
#            if conf['DELDEFAULTROUTE'] == 'enabled':
#                self.DefRoute = true
#            else:
#                self.DefRoute = false

        
        if conf.has_key('PPPOPTIONS'):
            self.createPPPOptions()
            
            options = conf['PPPOPTIONS']
            for o in string.split(options):
                self.PPPOptions[self.PPPOptions.addPPPOption()] = o

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
        
        self.Compression.load(conf)
        
        if conf.has_key('CALLBACK'):
            if conf['CALLBACK'] == 'on' or conf['CALLBACK'] == 'out' :
                callback = self.createCallback()
                callback.load(conf)
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

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = 'on'
            else:
                conf[confkey] = 'off'

        # DEFROUTE alway yes by ISDN
        conf['DEFROUTE'] = 'yes'

        if conf.has_key('PEERDNS') and conf['PEERDNS'] == "yes":
            if conf['DNS1']: del conf['DNS1']
            if conf['DNS2']: del conf['DNS2']

        if self.PPPOptions:
            opt = ""
            for i in xrange(len(self.PPPOptions)):
                if opt != "": opt = opt + ' '
                opt = opt + self.PPPOptions[i]
            conf['PPPOPTIONS'] = opt
        else:
            del conf['PPPOPTIONS']

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
            conf['CALLBACK'] == 'out'
            self.Callback.save(conf)
        else:
            conf['CALLBACK'] == 'off'
            if conf.has_key('PHONE_IN'): del conf['PHONE_IN']
            if conf.has_key('CBHUP'): del conf['CBHUP']
            if conf.has_key('CBDELAY'): del conf['CBDELAY']
            if conf.has_key('CBCP'): del conf['CBCP']
            if conf.has_key('SECURE'): del conf['SECURE']

        for i in conf.keys():
            if not conf[i]: del conf[i]
        
        conf.write()
        
    
class ModemDialup(Dialup):
    boolwvdict = { 'StupidMode' : 'Stupid Mode', }

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


        for selfkey in self.boolwvdict.keys():
            confkey = self.boolwvdict[selfkey]
            value = None
            if conf.has_key(sectname) and conf[sectname].has_key(confkey):
                value = conf[sectname][confkey]
            elif conf.has_key('Dialer Defaults') \
               and conf['Dialer Defaults'].has_key(confkey):
                value = conf['Dialer Defaults'][confkey]
                
            if value and value != '0':
                self.__dict__[selfkey] = true
            else:
                self.__dict__[selfkey] = false

        #
        # Read Modem Init strings
        #
        if not self.InitStrings: self.createInitStrings()
        for i in xrange(1, 10) :
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
                

        if self.Compression:
            self.Compression.load(parentConf)            

        if parentConf.has_key('PROVIDER'):
            self.ProviderName = parentConf['PROVIDER']
            
        if parentConf.has_key('PPPOPTIONS'):
            self.createPPPOptions()
            
            options = parentConf['PPPOPTIONS']
            for o in string.split(options):
                self.PPPOptions[self.PPPOptions.addPPPOption()] = o

        #
        # Workaround for backporting rp3-config stuff
        #
        if conf.has_key(sectname) and conf[sectname].has_key('Inherits'):
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
            #devname = parent.Device
            #name = parent.DeviceId
            devname = parent.Name
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
            sectname = 'Dialer ' + parentConf['WVDIALSECT']

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
        

        for selfkey in self.boolwvdict.keys():
            confkey = self.boolwvdict[selfkey]
            if self.__dict__[selfkey]:
                conf[sectname][confkey] = '1'
            else:
                if conf[sectname].has_key(confkey):
                    del conf[sectname][confkey] 
        

        #
        # Write Modem Init strings
        #
        if conf[sectname].has_key('Init'):
            del conf[sectname]['Init']
        if self.InitStrings:
            for i in xrange(1, min([len(self.InitStrings), 9]) + 1):
                confkey = 'Init'
                if i: confkey = confkey + str(i)                
            
                if self.InitStrings[i - 1]:
                    conf[sectname][confkey] = str(self.InitStrings[i - 1])
                else:
                    if conf[sectname].has_key(confkey):
                        del conf[sectname][confkey]


        if self.PPPOptions:
            opt = ""
            for i in xrange(len(self.PPPOptions)):
                if opt != "": opt = opt + ' '
                opt = opt + self.PPPOptions[i]
            #print opt
            parentConf['PPPOPTIONS'] = opt


        if self.Persist:
            parentConf['PERSIST'] = 'yes'
        else:
            parentConf['PERSIST'] = 'no'

        if self.DefRoute:
            parentConf['DEFROUTE'] = 'yes'
        else:
            parentConf['DEFROUTE'] = 'no'

        if self.ProviderName:
            parentConf['PROVIDER'] = self.ProviderName

        if parent.Name:
            hwlist = NCHardwareList.getHardwareList()
            for hw in hwlist:
                if hw.Name == parent.Name:
                    if hw.Modem:
                        parentConf['MODEMPORT'] = str(hw.Modem.DeviceName)
                        break


        conf[sectname]['Inherits'] = devname

        for i in conf.keys():
            if not conf[i]: del conf[i]

        conf.write()

        if self.Compression:
            self.Compression.save(parentConf)            

if __name__ == '__main__':
    dev = Device()
    dev.load('tdslHomeTonline')
    print dev.Dialup.Login
    dev.save()
