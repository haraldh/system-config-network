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
import os
import os.path

import NCDeviceList
import NCHardwareList

from ProfileList import *

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

import Conf

class ProfileList(ProfileList_base):
    def __init__(self, list = None, parent = None):
        ProfileList_base.__init__(self, list, parent)        

    def load(self):
        devicelist = NCDeviceList.getDeviceList()

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
               if dev[:6] != 'ifcfg-':
                   continue
               for d in devicelist:
                   if d.DeviceId == dev[6:]:
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
        self.commit()

    def save(self):
        devicelist = NCDeviceList.getDeviceList()

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

        devlist = os.listdir(OLDSYSCONFDEVICEDIR)
        for dev in devlist:
            if dev[:6] != 'ifcfg-':
                continue
            if os.path.islink(OLDSYSCONFDEVICEDIR+'/'+dev):
                try:
                    os.unlink(OLDSYSCONFDEVICEDIR+'/'+dev)
                except:
                    pass

        for prof in self.data:
            try:
                os.mkdir(SYSCONFPROFILEDIR + '/' + prof.ProfileName)
            except:
                pass

            nwconf = Conf.ConfShellVar(SYSCONFPROFILEDIR + '/' + prof.ProfileName + '/network')
            nwconf['HOSTNAME'] = prof.DNS.Hostname
            dnsconf.filename = SYSCONFPROFILEDIR + '/' + prof.ProfileName + '/resolv.conf'
            dnsconf['domain'] = [prof.DNS.Domainname]
            dnsconf['nameservers'] = []
            dnsconf['search'] = prof.DNS.SearchList
            if prof.DNS.PrimaryDNS != '':
                dnsconf['nameservers'].append(prof.DNS.PrimaryDNS)
            if prof.DNS.SecondaryDNS!= '':
                dnsconf['nameservers'].append(prof.DNS.SecondaryDNS)
            if prof.DNS.TernaryDNS != '':
                dnsconf['nameservers'].append(prof.DNS.TernaryDNS)

            hoconf.filename = SYSCONFPROFILEDIR + '/' + prof.ProfileName + '/hosts'
            for i in hoconf.keys():
                del hoconf[i]

            for host in prof.HostsList:
                hoconf[host.IP] = [host.Hostname, host.AliasList]

            nwconf.write()
            dnsconf.write()
            hoconf.write()

            for devId in prof.ActiveDevices:
                for dev in devicelist:
                    if dev.DeviceId == devId:
                        devName = dev.Device

                try:
                    os.unlink(SYSCONFPROFILEDIR+'/'+prof.ProfileName+'/ifcfg-'+devId)
                except:
                    pass

                try:
                    os.symlink(SYSCONFDEVICEDIR+'/ifcfg-'+devId, SYSCONFPROFILEDIR+'/'+prof.ProfileName+'/ifcfg-'+devId)
                except:
                    pass

                if prof.Active == false and prof.ProfileName != 'default':
                    continue

                try:
                    os.unlink(OLDSYSCONFDEVICEDIR+'/ifcfg-'+devName)
                except:
                    pass

                try:
                    os.symlink(SYSCONFPROFILEDIR+'/'+prof.ProfileName+'/ifcfg-'+devId, OLDSYSCONFDEVICEDIR+'/ifcfg-'+devName)
                except:
                    print 'Darn, symlinking device '+devName+','+devId+' failed...'

            if prof.Active == false:
                continue

            if os.path.isfile('/etc/resolv.conf') and not os.path.islink('/etc/resolv.conf'):
                os.rename('/etc/resolv.conf', '/etc/resolv.conf.bak')

            try:
                os.unlink('/etc/resolv.conf')
            except:
                pass

            try:
                os.symlink(SYSCONFPROFILEDIR + '/' + prof.ProfileName + '/resolv.conf', '/etc/resolv.conf')
            except:
                pass

            if os.path.isfile('/etc/hosts') and not os.path.islink('/etc/hosts'):
                os.rename('/etc/hosts', '/etc/hosts.bak')

            try:
                os.unlink('/etc/hosts')
            except:
                pass

            try:
                os.symlink(SYSCONFPROFILEDIR + '/' + prof.ProfileName + '/hosts', '/etc/hosts')
            except:
                pass

    def activateDevice (self, deviceid, profile, state=None):
        devicelist = NCDeviceList.getDeviceList()
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.ProfileName != profile:
                continue
            if state:
                if deviceid not in prof.ActiveDevices:
                    prof.ActiveDevices.append(deviceid)
            else:
                if deviceid in prof.ActiveDevices:
                    del prof.ActiveDevices[prof.ActiveDevices.index(deviceid)]

    def switchToProfile(self, val):
        devicelist = NCDeviceList.getDeviceList()
        hardwarelist = NCHardwareList.getHardwareList()
        profilelist = getProfileList()

        found = false
        for prof in profilelist:
            if prof.ProfileName == val:
                found = true
                break

        if found == false:
            print "No Profile with name "+val+" could be found."
            return

        for prof in profilelist:
            if prof.ProfileName == val:
                prof.Active = true
            else:
                prof.Active = false

        print "Switching to Profile "+val

        devicelist.save()
        hardwarelist.save()
        profilelist.save()


PFList = None

def getProfileList():
    global PFList
    if PFList == None:
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
