from DeviceList import *
from NC_functions import *
from os.path import *
from ConfSMB import *

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

import Conf
        
class Dialup(Dialup_base):
    def __init__(self, list = None, parent = None):
        Dialup_base.__init__(self, list, parent)        

class IsdnDialup(Dialup):                        
    def __init__(self, list = None, parent = None):
        Dialup.__init__(self, list, parent)        

    def load(self, parentConf):
        devdir = SYSCONFDEVICEDIR + name + '.d/'
        if not isdir(devdir):
            return

    def save(self, parentConf):
        devdir = SYSCONFDEVICEDIR + name + '.d/'
        if not isdir(devdir):
            os.mkdir(devdir)

class ModemDialup(Dialup):
    wvdict = { 'Login' : 'Username',
               'Password' : 'Password',
               'Prefix' : 'Dial Prefix',
               'Areacode' : 'Area Code',
               'PhoneOut' : 'Phone',
               }                   
                        
    def __init__(self, list = None, parent = None):
        Dialup.__init__(self, list, parent)                

    def load(self, parentConf):
        parent = self.getParent()

        if parent:
            name = parent.DeviceId
            
        if parentConf.has_key('WVDIALSECT'):
            name = parentConf['WVDIALSECT']

        conf = ConfSMB(filename = '/etc/wvdial.conf')
        
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
                print selfkey + " = " + value
                self.__dict__[selfkey] = value

        #
        # Read Modem Init strings
        #
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
                if not self.InitStrings: self.createInitStrings()
                print confkey + " = " + value
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
        conf = ConfSMB(filename = '/etc/wvdial.conf')
        
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
        print "device = " + name
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
                    print conf.getline()                    
                    break
                    
                conf.nextline()
            conf.write()


if __name__ == '__main__':
    dev = Device()
    dev.load('ppp1')
    dev.Dialup.Password = "Hello"
    dev.commit()
    dev.save()
