import HardwareList
import DeviceList
from ProfileList import *
from os import *
from os.path import *

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

import Conf

class ProfileList(ProfileList_base):
    def __init__(self, list = None, parent = None):
        ProfileList_base.__init__(self, list, parent)        

    def load(self):
        nwconf = Conf.ConfShellVar('/etc/sysconfig/network')
        hoconf = Conf.ConfEHosts()
        dnsconf = Conf.ConfEResolv()
        curr_prof = nwconf['CURRENT_PROFILE']
        if curr_prof == None or curr_prof == '':
            curr_prof = 'default'

        proflist = os.listdir(SYSCONFPROFILEDIR)
        for pr in proflist:
            nwconf = Conf.ConfShellVar(SYSCONFPROFILEDIR + '/' + pr + '/network')
            i = self.addProfile()
            prof = self.data[i]
            prof.createActiveDevices()
            prof.createDNS()
            prof.createHostsList()
            prof.ProfileName = pr
            if pr == curr_prof:
                prof.Active = true
            else:
                prof.Active = false
            devlist = os.listdir(SYSCONFPROFILEDIR + '/' + pr)
            for dev in devlist:
               if dev[:6] == 'ifcfg-':
                   prof.ActiveDevices.append(dev[6:])
            hoconf.filename = SYSCONFPROFILEDIR + '/' + pr + '/hosts'
            hoconf.read()
            for ip in hoconf.keys():
                host = Host()
                host.createAliasList()
                host.IP = ip
                host.Hostname = hoconf[ip][0]
                for al in hoconf[ip][1]:
                    host.AliasList.append(al);
                prof.HostsList.append(host)
            dnsconf.filename = SYSCONFPROFILEDIR + '/' + pr + '/resolv.conf'
            dnsconf.read()
            prof.DNS.Hostname     = ''
            prof.DNS.Domainname   = ''
            prof.DNS.PrimaryDNS   = ''
            prof.DNS.SecondaryDNS = ''
            prof.DNS.TernaryDNS   = ''
            prof.DNS.Hostname     = nwconf['HOSTNAME']
            if len(dnsconf['domain']) > 0:
                prof.DNS.Domainname   = dnsconf['domain'][0]
            if dnsconf.has_key('nameservers'):
                prof.DNS.PrimaryDNS = dnsconf['nameservers'][0]
                if len(dnsconf['nameservers']) > 1:
                    prof.DNS.SecondaryDNS = dnsconf['nameservers'][1]
                if len(dnsconf['nameservers']) > 2:
                    prof.DNS.TernaryDNS = dnsconf['nameservers'][2]
            sl = prof.DNS.createSearchList()
            if dnsconf.has_key('search'):
                for ns in dnsconf['search']:
                    sl.append(ns)

    def save(self):
        devicelist = DeviceList.getDeviceList()
        hardwarelist = HardwareList.getHardwareList()

        nwconf = Conf.ConfShellVar('/etc/sysconfig/network')
        hoconf = Conf.ConfEHosts()
        dnsconf = Conf.ConfEResolv()

        try:
            os.system('/bin/rm -rf '+SYSCONFPROFILEDIR)
        except:
            pass

        try:
            os.mkdir(SYSCONFPROFILEDIR)
        except:
            pass

        for prof in self.data:
            try:
                mkdir(SYSCONFPROFILEDIR + '/' + prof.ProfileName)
            except:
                pass

            nwconf = Conf.ConfShellVar(SYSCONFPROFILEDIR + '/' + prof.ProfileName + '/network')
            nwconf['HOSTNAME'] = prof.DNS.Hostname
            dnsconf.filename = SYSCONFPROFILEDIR + '/' + prof.ProfileName + '/resolv.conf'
            dnsconf['domain'] = [prof.DNS.Domainname]
            dnsconf['nameservers'] = []
            if prof.DNS.PrimaryDNS != '':
                dnsconf['nameservers'].append(prof.DNS.PrimaryDNS)
            if prof.DNS.SecondaryDNS!= '':
                dnsconf['nameservers'].append(prof.DNS.SecondaryDNS)
            if prof.DNS.TernaryDNS != '':
                dnsconf['nameservers'].append(prof.DNS.TernaryDNS)
            nwconf.write()
            dnsconf.write()

            if prof.Active == false and prof.ProfileName != 'default':
                continue

            for devId in prof.ActiveDevices:
                for dev in devicelist:
                    if dev.DeviceId == devId:
                        devName = dev.Device

                try:
                    os.unlink(OLDSYSCONFDEVICEDIR+'/ifcfg-'+devName)
                except:
                    pass

                try:
                    os.unlink(SYSCONFPROFILEDIR+'/'+prof.ProfileName+'/ifcfg-'+devId)
                except:
                    pass

                try:
                    os.symlink(SYSCONFDEVICEDIR+'/ifcfg-'+devId, SYSCONFPROFILEDIR+'/'+prof.ProfileName+'/ifcfg-'+devId)
                    os.symlink(SYSCONFPROFILEDIR+'/'+prof.ProfileName+'/ifcfg-'+devId, OLDSYSCONFDEVICEDIR+'/ifcfg-'+devName)
                except:
                    print 'Darn, symlinking device '+devName+','+devId+' failed...'


PFList = None

def getProfileList():
    global PFList
    if not PFList:
        PFList = ProfileList()
        PFList.load()
    return PFList


if __name__ == '__main__':
    pl = ProfileList()
    pl.load()
    for i in xrange(len(pl)):
        print "Device: " + str(pl[i].DeviceId)
        print "DevName: " + str(pl[i].DeviceName)
        print "IP: " + str(pl[i].IP)
        print "OnBoot: " + str(pl[i].OnBoot)
        print "---------"

    pl.save()
