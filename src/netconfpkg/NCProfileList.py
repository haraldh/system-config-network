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
        nwconf = Conf.ConfShellVar("/etc/sysconfig/network")
        hoconf = Conf.ConfEHosts()
        dnsconf = Conf.ConfEResolv()
        try:
            curr_prof = nwconf['CURRENT_PROFILE']
        except:
            curr_prof = 'default'

        proflist = os.listdir(SYSCONFPROFILEDIR)
        for pr in proflist:
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
            prof.DNS.PrimaryDNS = ''
            prof.DNS.SecondaryDNS = ''
            prof.DNS.TernaryDNS = ''
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
        pass

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
