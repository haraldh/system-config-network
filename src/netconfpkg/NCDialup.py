from DeviceList import *
from NC_functions import *
from os.path import *
from ConfSMB import *

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
        
        
class ModemDialup(Dialup_base):
    wvdict = { 'Login' : 'Username',
               'Password' : 'Password',
               'Prefix' : 'Dial Prefix',
               'Areacode' : 'Area Code',
               'PhoneOut' : 'Phone',
               }                   
                        
    def __init__(self, list = None, parent = None):
        Dialup_base.__init__(self, list, parent)        

    def load(self, name):
        #devdir = SYSCONFDEVICEDIR + name + '.d/'
        #if not isdir(devdir):
        #    return
        
        conf = ConfSMB(filename = '/etc/wvdial.conf')
        #          for sect in conf.keys():
        #              for key in conf[sect].keys():
        #                  print "conf[" + sect + "][" + key + "] = " + conf[sect][key]
        
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
        
    def save(self):
        #devdir = SYSCONFDEVICEDIR + name + '.d/'
        #if not isdir(devdir):
        #    os.mkdir(devdir)
        #
        #conf = ConfSMB(filename = '/etc/wvdial.conf')
        pass

if __name__ == '__main__':
    dl = ModemDialup()
    dl.load('phone2')
    dl.save()
