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
import shutil

import NCDeviceList
import NCHardwareList

from NC_functions import _
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
        use_hostname = nwconf['HOSTNAME']
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
            prof.DNS.Hostname     = use_hostname
            prof.DNS.Domainname   = ''
            prof.DNS.PrimaryDNS   = ''
            prof.DNS.SecondaryDNS = ''
            prof.DNS.TertiaryDNS  = ''
            if nwconf['HOSTNAME'] != '':
                prof.DNS.Hostname     = nwconf['HOSTNAME']
            if len(dnsconf['domain']) > 0:
                prof.DNS.Domainname   = dnsconf['domain'][0]
            if dnsconf.has_key('nameservers'):
                prof.DNS.PrimaryDNS = dnsconf['nameservers'][0]
                if len(dnsconf['nameservers']) > 1:
                    prof.DNS.SecondaryDNS = dnsconf['nameservers'][1]
                if len(dnsconf['nameservers']) > 2:
                    prof.DNS.TertiaryDNS = dnsconf['nameservers'][2]
            sl = prof.DNS.createSearchList()
            if dnsconf.has_key('search'):
                for ns in dnsconf['search']:
                    sl.append(ns)
        self.commit()

    def test(self):
        self.fixInterfaces()
        devmap = {}
        devicelist = NCDeviceList.getDeviceList()
        
        for prof in self:
            if not prof.Active:
                continue
            for devId in prof.ActiveDevices:
                for dev in devicelist:
                    if dev.DeviceId == devId:
                        device = dev
                        break
                else:
                    continue
            
                if devmap.has_key(device.Device):
                    msg = (_('Device %s uses the same Hardware Device "%s" like %s!\n') \
                          + _('Please select another Hardware Device or \nactivate only one of them.')) % (device.DeviceId, device.Device, devmap[device.Device].DeviceId)
                    raise TestError(msg)

                devmap[device.Device] = device
            break
        
    def fixInterfaces(self):
        pppnum = 0
        ipppnum = 0
        isdnnum = 0
        devicelist = NCDeviceList.getDeviceList()
        changed = 0
        for prof in self:
            if not prof.Active:
                continue
            for devid in prof.ActiveDevices:
                for dev in devicelist:
                    if dev.DeviceId != devid:
                        continue
                        
                    if dev.Type == "Modem" or dev.Type == 'xDSL':
                        dstr = "ppp"+str(pppnum)
                        if dev.Device != dstr:                            
                            dev.Device = dstr
                            changed = 1
                        pppnum = pppnum + 1
                    elif  dev.Type == "ISDN":
                        if dev.Dialup.EncapMode == 'syncppp':
                            dstr = "ippp"+str(ipppnum)
                            if dstr != dev.Device:
                                dev.Device = dstr
                                changed = 1
                            if dev.Dialup.ChannelBundling == true:
                                ipppnum = ipppnum + 1
                                dstr = "ippp"+str(ipppnum)
                                if dstr != dev.Dialup.SlaveDevice:
                                    dev.Dialup.SlaveDevice = dstr
                                    changed = 1
                            ipppnum = ipppnum + 1
                        else:
                            dstr = "isdn"+str(isdnnum)
                            if dstr != dev.Device:
                                dev.Device = dstr
                                changed = 1
                            isdnnum = isdnnum + 1
                    break
            break
        
        if changed:
            devicelist.save()

    def save(self):
        self.test()
        devicelist = NCDeviceList.getDeviceList()

        nwconf = Conf.ConfShellVar('/etc/sysconfig/network')
        hoconf = Conf.ConfEHosts()
        dnsconf = Conf.ConfEResolv()

        for prof in self.data:
            if prof.Active == true:
                break

        nwconf['HOSTNAME'] = prof.DNS.Hostname

        if prof.ProfileName != 'default':
            nwconf['CURRENT_PROFILE'] = prof.ProfileName
        else:
            del nwconf['CURRENT_PROFILE']

        nwconf.write()

        try:
            os.mkdir(SYSCONFPROFILEDIR)
        except:
            pass

        # Remove all profile directories except default
        proflist = os.listdir(SYSCONFPROFILEDIR)
        for prof in proflist:
            if prof == 'default':
                continue

            try:
                shutil.rmtree(SYSCONFPROFILEDIR+'/'+prof)
            except:
                pass

        # Remove all files in the default profile directory
        filelist = os.listdir(SYSCONFPROFILEDIR+'/default')
        for file in filelist:
            try:
                os.unlink(OLDSYSCONFDEVICEDIR+'/default/'+file)
            except:
                pass

        devlist = os.listdir(OLDSYSCONFDEVICEDIR)
        for dev in devlist:
            if dev[:6] != 'ifcfg-' or dev == 'ifcfg-lo':
                continue
            if os.path.islink(OLDSYSCONFDEVICEDIR+'/'+dev) or ishardlink(OLDSYSCONFDEVICEDIR+'/'+dev):
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

            dnsconf['domain'] = ''
            if prof.DNS.Domainname != '':
                dnsconf['domain'] = [prof.DNS.Domainname]
            else:
                del dnsconf['domain']

            dnsconf['search'] = []
            if prof.DNS.SearchList != []:
                dnsconf['search'] = prof.DNS.SearchList
            else:
                del dnsconf['search']

            dnsconf['nameservers'] = []
            nameservers = []
            if prof.DNS.PrimaryDNS != '':
                nameservers.append(prof.DNS.PrimaryDNS)
            if prof.DNS.SecondaryDNS != '':
                nameservers.append(prof.DNS.SecondaryDNS)
            if prof.DNS.TertiaryDNS != '':
                nameservers.append(prof.DNS.TertiaryDNS)

            dnsconf['nameservers'] = nameservers

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
                        if dev.Type == "CIPE":
                            devName = dev.DeviceId
                        else:
                            devName = dev.Device
                        break

                try:
                    os.unlink(SYSCONFPROFILEDIR+'/'+prof.ProfileName+'/ifcfg-'+devId)
                except:
                    pass

                try:
                    os.link(SYSCONFDEVICEDIR+'/ifcfg-'+devId, SYSCONFPROFILEDIR+'/'+prof.ProfileName+'/ifcfg-'+devId)
                except:
                    pass

                if prof.Active == false and prof.ProfileName != 'default':
                    continue

                try:
                    os.unlink(OLDSYSCONFDEVICEDIR+'/ifcfg-'+devName)
                except:
                    pass

                try:
                    os.link(SYSCONFPROFILEDIR+'/'+prof.ProfileName+'/ifcfg-'+devId, OLDSYSCONFDEVICEDIR+'/ifcfg-'+devName)
                except:
                    print 'Darn, linking device '+str(devName)+','+str(devId)+' failed...'

            if prof.Active == false:
                continue

            if os.path.isfile('/etc/resolv.conf') and not ishardlink('/etc/resolv.conf') and not os.path.islink('/etc/resolv.conf'):
                os.rename('/etc/resolv.conf', '/etc/resolv.conf.bak')

            try:
                os.unlink('/etc/resolv.conf')
            except:
                pass

            try:
                os.link(SYSCONFPROFILEDIR + '/' + prof.ProfileName + '/resolv.conf', '/etc/resolv.conf')
            except:
                pass

            if os.path.isfile('/etc/hosts') and not ishardlink('/etc/hosts') and not os.path.islink('/etc/hosts'):
                os.rename('/etc/hosts', '/etc/hosts.bak')

            try:
                os.unlink('/etc/hosts')
            except:
                pass

            try:
                os.link(SYSCONFPROFILEDIR + '/' + prof.ProfileName + '/hosts', '/etc/hosts')
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
