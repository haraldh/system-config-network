## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>

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
import string

import NCDeviceList
import NCIPsecList
import NCHardwareList

from NC_functions import *
from netconfpkg import ProfileList_base
from netconfpkg import Profile
from netconfpkg import Host

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

from rhpl import Conf
from rhpl.log import log

from types import ListType

class MyFileList(ListType):
    def __setitem__(self, key, value):
        value = os.path.abspath(value)
        log.log(5, "MyFileList.__setitem__(self, %s, %s)" % (str(key),
                                                             str(value)))
        return ListType.__setitem__(self, key, value)

    def __contains__(self, obj):
        obj = os.path.abspath(obj)
        ret = ListType.__contains__(self, os.path.abspath(obj))
        log.log(5, "MyFileList.__contains__(self, %s) == %s" % (str(obj), str(ret)))
        return ret

    def append(self, obj):
        obj = os.path.abspath(obj)
        log.log(5, "MyFileList.append(self, %s)" % str(obj))
        return ListType.append(self, os.path.abspath(obj))

class ProfileList(ProfileList_base):
    def __init__(self, list = None, parent = None):
        ProfileList_base.__init__(self, list, parent)        
    
    def load(self):
        changed = updateNetworkScripts()
        self.__delslice__(0, len(self))

        self.curr_prof = 'default'
        nwconf = Conf.ConfShellVar(netconfpkg.ROOT + SYSCONFNETWORK)
        if nwconf.has_key('CURRENT_PROFILE'):
            self.curr_prof = nwconf['CURRENT_PROFILE']
            
        if nwconf.has_key('HOSTNAME'):
            self.use_hostname = nwconf['HOSTNAME']
        else:
            self.use_hostname = 'localhost'
            
        if self.curr_prof == None or self.curr_prof == '':
            self.curr_prof = 'default'

        proflist = []
        if os.path.isdir(netconfpkg.ROOT + SYSCONFPROFILEDIR):
            proflist = os.listdir(netconfpkg.ROOT + SYSCONFPROFILEDIR)        
            for pr in proflist:
                # 60016
                profdir = netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + pr
                if not os.path.isdir(profdir):
                    continue
                self.loadprof(pr, profdir)
        else:
            self.loadprof('default', None)

        prof = self.getActiveProfile()
        prof.DNS.Hostname = self.use_hostname        
        self.commit(changed)

    def loadprof(self, pr, profdir):        
        devicelist = NCDeviceList.getDeviceList()
        ipseclist = NCIPsecList.getIPsecList()

        i = self.addProfile()
        prof = self[i]
        prof.createActiveDevices()
        prof.createActiveIPsecs()
        prof.createDNS()
        prof.createHostsList()
        prof.ProfileName = pr
        if pr == self.curr_prof:
            prof.Active = true
        else:
            prof.Active = false

        if profdir:
            devlist = ConfDevices(profdir)
        else:
            devlist = ConfDevices(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR)
            
        for dev in devlist:
            for d in devicelist:
                if d.DeviceId == dev:
                    prof.ActiveDevices.append(dev)
                    break

        for ipsec in devlist:
            for d in ipseclist:
                if d.IPsecId == ipsec:
                    prof.ActiveIPsecs.append(ipsec)
                    break

        if profdir:
            hoconf = Conf.ConfFHosts( filename = profdir + '/hosts')
        else:
            hoconf = Conf.ConfFHosts( filename = HOSTSCONF )
            
        hoconf.read()
        hoconf.rewind()
        while hoconf.findnextcodeline():
            try:
                harray = hoconf.getfields()
                host = Host()
                host.createAliasList()
                host.Hostname = harray[1]
                host.IP = harray[0]
                for al in harray[2:]:
                    host.AliasList.append(al);
                prof.HostsList.append(host)
                hoconf.nextline()
            except:
                break
            
        dnsconf = Conf.ConfEResolv()
        if profdir:
            dnsconf.filename = profdir + '/resolv.conf'
        else:
            dnsconf.filename = netconfpkg.ROOT + RESOLVCONF
        dnsconf.read()
        prof.DNS.Hostname     = self.use_hostname
        prof.DNS.Domainname   = ''
        prof.DNS.PrimaryDNS   = ''
        prof.DNS.SecondaryDNS = ''
        prof.DNS.TertiaryDNS  = ''

        if profdir:
            nwconf = Conf.ConfShellVar(profdir + '/network')
        else:
            nwconf = Conf.ConfShellVar(netconfpkg.ROOT + SYSCONFNETWORK)
            
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

    def test(self):
        return
        # Keep that test for later versions
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
            
                if devmap.has_key(device.Device) and \
                       device.Alias == devmap[device.Device].Alias:
                    msg = (_('Device %s uses the same Hardware Device '
                             '"%s" like %s!\n') \
                          + _('Please select another Hardware Device or \n'
                              'activate only one of them.')) % \
                              (device.DeviceId, device.Device, \
                               devmap[device.Device].DeviceId)
                    raise TestError(msg)

                devmap[device.Device] = device
            break
        
    def commit(self, changed=true):        
        self.test()
        ProfileList_base.commit(self, changed)
        
    def fixInterfaces(self):
        return
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
                        
                    if dev.Type == MODEM or dev.Type == DSL:
                        dstr = "ppp"+str(pppnum)
                        if dev.Device != dstr:                            
                            dev.Device = dstr
                            changed = 1
                        pppnum = pppnum + 1
                    elif  dev.Type == ISDN:
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
        
    def save(self):
        import socket
        # Just to be safe...
        os.umask(0022)

	# commit the changes
        self.commit(changed=false)

        devicelist = NCDeviceList.getDeviceList()

        nwconf = Conf.ConfShellVar(netconfpkg.ROOT + SYSCONFNETWORK)
        dnsconf = Conf.ConfEResolv()

        act_prof = self.getActiveProfile()		
        
        if socket.gethostname() != act_prof.DNS.Hostname:
            # if the hostname changed, set it system wide (#55746)
            os.system("hostname %s" % act_prof.DNS.Hostname)
            log.log(2, "change hostname to %s" % act_prof.DNS.Hostname)
            newip = '127.0.0.1'
            try:
                newip = socket.gethostbyname(act_prof.DNS.Hostname)
            except:
                for host in act_prof.HostsList:
                    if host.IP == '127.0.0.1':
                        host.Hostname = 'localhost.localdomain'
                        host.AliasList = [ act_prof.DNS.Hostname,
                                           'localhost']
                        if act_prof.DNS.Hostname.find(".") != -1:
                            host.AliasList.append(act_prof.DNS.Hostname.split(".")[0])
            else:
                for host in act_prof.HostsList:
                    if host.IP == '127.0.0.1':
                        host.Hostname = 'localhost.localdomain'
                        host.AliasList = [ 'localhost' ]
                    if host.IP == newip:
                        host.AliasList = []
                        try:
                            hname = socket.gethostbyaddr(newip)
                            host.Hostname = hname[0]
                            host.AliasList.extend(hname[1])
                        except:
                            host.Hostname = act_prof.DNS.Hostname
                        if host.Hostname != act_prof.DNS.Hostname:
                            host.AliasList.append( act_prof.DNS.Hostname )
                        if act_prof.DNS.Hostname.find(".") != -1:
                            host.AliasList.append(act_prof.DNS.Hostname.split(".")[0])
                            
        nwconf['HOSTNAME'] = act_prof.DNS.Hostname
              
        if act_prof.ProfileName != 'default':
            nwconf['CURRENT_PROFILE'] = act_prof.ProfileName
        else:
            del nwconf['CURRENT_PROFILE']

        nwconf.write()

        if not os.path.isdir(netconfpkg.ROOT + SYSCONFPROFILEDIR):
            mkdir(netconfpkg.ROOT + SYSCONFPROFILEDIR)

        files_used = MyFileList()
                
        for prof in self:
            if not os.path.isdir(netconfpkg.ROOT + SYSCONFPROFILEDIR + \
                                 '/' + prof.ProfileName):
                mkdir(netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + \
                      prof.ProfileName)
            files_used.append(netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + \
                              prof.ProfileName)

            nwconf = Conf.ConfShellVar(netconfpkg.ROOT + SYSCONFPROFILEDIR + \
                                       '/' + prof.ProfileName + '/network')
            nwconf.write()
            files_used.append(nwconf.filename)


            nwconf['HOSTNAME'] = prof.DNS.Hostname
            
            dnsconf.filename = netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + \
                               prof.ProfileName + '/resolv.conf'

            files_used.append(dnsconf.filename)
            
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

            hoconf = Conf.ConfFHosts(filename = netconfpkg.ROOT + \
                                     SYSCONFPROFILEDIR + '/' + \
                                     prof.ProfileName + \
                                     '/hosts')
            files_used.append(hoconf.filename)
            saved = []
            hoconf.fsf()
            for host in prof.HostsList:
                hoconf[host.Hostname] = [host.IP, host.AliasList]
                saved.append(host.Hostname)
                
            for i in hoconf.keys():
                if not i in saved:
                    # delete all other entries the user has deleted in the UI
                    del hoconf[i]

            del saved

            dnsconf.write()
            hoconf.write()

            del hoconf
            
            for devId in prof.ActiveDevices:
                for prefix in [ 'ifcfg-', 'route-', 'keys-']:
                    devfilename = netconfpkg.ROOT + SYSCONFDEVICEDIR + \
                                  prefix + devId
                    profilename = netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + \
                                  prof.ProfileName + '/' + prefix + devId
                    unlink(profilename)

                    link(devfilename, profilename)
                    files_used.append(devfilename)
                    files_used.append(profilename)

                # unlink old .route files
                profilename = netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + \
                              prof.ProfileName + '/' + devId + '.route'
                unlink(profilename)

                    
                if prof.Active == false and prof.ProfileName != 'default':
                    continue

                # Active Profile or default profile                
                for prefix in [ 'ifcfg-', 'route-', 'keys-' ]:
                    devfilename = netconfpkg.ROOT + SYSCONFDEVICEDIR + \
                                      '/' + prefix + devId
                    profilename = netconfpkg.ROOT + OLDSYSCONFDEVICEDIR + \
                                  '/' + prefix + devId
                       
                    if os.path.isfile(devfilename):
                        unlink(profilename)
                        link(devfilename, profilename)
                        files_used.append(profilename)

                # unlink old .route files
                unlink(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR + \
                       '/' + devId + '.route')

            for devId in prof.ActiveIPsecs:
                for prefix in [ 'ifcfg-', 'keys-']:
                    devfilename = netconfpkg.ROOT + SYSCONFDEVICEDIR + \
                                  prefix + devId
                    profilename = netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + \
                                  prof.ProfileName + '/' + prefix + devId
                    unlink(profilename)

                    link(devfilename, profilename)
                    files_used.append(devfilename)
                    files_used.append(profilename)

                if prof.Active == false and prof.ProfileName != 'default':
                    continue

                # Active Profile or default profile                
                for prefix in [ 'ifcfg-', 'keys-' ]:
                    devfilename = netconfpkg.ROOT + SYSCONFDEVICEDIR + \
                                      '/' + prefix + devId
                    profilename = netconfpkg.ROOT + OLDSYSCONFDEVICEDIR + \
                                  '/' + prefix + devId
                       
                    if os.path.isfile(devfilename):
                        unlink(profilename)
                        link(devfilename, profilename)
                        files_used.append(profilename)                

            if prof.Active == false:                
                continue

            # Special actions for the active profile

            if os.path.isfile(netconfpkg.ROOT + RESOLVCONF) and not \
                   ishardlink(netconfpkg.ROOT + RESOLVCONF) and not \
                   os.path.islink(netconfpkg.ROOT + RESOLVCONF):
                rename(netconfpkg.ROOT + RESOLVCONF, netconfpkg.ROOT + \
                       RESOLVCONF + '.bak')
            else:
                unlink(netconfpkg.ROOT + RESOLVCONF)

            link(netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + \
                 prof.ProfileName + \
                 '/resolv.conf', netconfpkg.ROOT + RESOLVCONF)
            os.chmod(netconfpkg.ROOT + RESOLVCONF, 0644)
                
            if os.path.isfile(netconfpkg.ROOT + HOSTSCONF) \
                   and not ishardlink(netconfpkg.ROOT + HOSTSCONF) \
                   and not os.path.islink(netconfpkg.ROOT + HOSTSCONF):
                rename(netconfpkg.ROOT + HOSTSCONF, netconfpkg.ROOT + \
                       HOSTSCONF + '.bak')
            else:
                unlink(netconfpkg.ROOT + HOSTSCONF)

            link(netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + \
                 prof.ProfileName + '/hosts', \
                 netconfpkg.ROOT + HOSTSCONF)
            os.chmod(netconfpkg.ROOT + HOSTSCONF, 0644)        

        # Remove all unused files that are linked in the device directory
        devlist = os.listdir(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR)
        for dev in devlist:
            if string.split(dev, '-')[0] not in [ 'ifcfg', 'route',
                                                  'keys' ] \
                                                  or dev == 'ifcfg-lo':
                continue
            file = netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+'/'+dev
            if file in files_used:
                # Do not remove used files
                continue
            stat = os.stat(file)
            if stat[3] > 1:
                # Check, if it is a device of neat in every profile directory
                dirlist = os.listdir(netconfpkg.ROOT + SYSCONFPROFILEDIR)
                for dir in dirlist:
                    dirname = netconfpkg.ROOT + SYSCONFPROFILEDIR + '/' + dir
                    if not os.path.isdir(dirname):
                        continue
                    filelist = os.listdir(dirname)                    
                    for file2 in filelist:
                        stat2 = os.stat(dirname + '/' + file2)
                        if os.path.samestat(stat, stat2):
                            unlink(file)

                        

        # Remove all profile directories except default
        proflist = os.listdir(netconfpkg.ROOT + SYSCONFPROFILEDIR)
        for prof in proflist:
            # Remove all files in the profile directory
            filelist = os.listdir(netconfpkg.ROOT + SYSCONFPROFILEDIR + prof)
            for file in filelist:
                filename = netconfpkg.ROOT + SYSCONFPROFILEDIR + prof + '/' + \
                           file
                if filename in files_used:
                    # Do not remove used files
                    continue                
                unlink(filename)

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

    def activateIpsec (self, ipsecid, profile, state=None):
        ipseclist = NCIPsecList.getIPsecList()
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.ProfileName != profile:
                continue
            if state:
                if ipsecid not in prof.ActiveIPsecs:
                    prof.ActiveIPsecs.append(ipsecid)
            else:
                if ipsecid in prof.ActiveIPsecs:
                    del prof.ActiveIPsecs[prof.ActiveIPsecs.index(ipsecid)]

    def switchToProfile(self, val, dochange = true):
        found = false
        aprof = None
        for prof in self:
            if (isinstance(val, str) and prof.ProfileName == val) or \
                   (isinstance(val, Profile) and prof == val) :
                    found = true
                    break
        else:
            return None

        modl = self.modified()
        for prof in self:
            mod = prof.modified()
            if (isinstance(val, str) and prof.ProfileName == val) or \
                   (isinstance(val, Profile) and prof == val) :
                prof.Active = true
                aprof = prof
            else:
                prof.Active = false
            if not dochange:
                prof.setChanged(mod)

        if not dochange:
            self.setChanged(mod)
        
        return prof

    def getActiveProfile(self):
        for prof in self:
            if not prof.Active:
                continue
            return prof

        if len(self):
            return self[0]

    def _objToStr(self, parentStr = None):
        retstr = ""
        for profile in self:
            retstr += profile._objToStr("ProfileList.%s" % \
                                        (profile.ProfileName))

        return retstr

    def _parseLine(self, vals, value):
        if len(vals) <= 1:
            return
        if vals[0] == "ProfileList":
            del vals[0]
        else:
            return
        for profile in self:
            if profile.ProfileName == vals[0]:
                profile._parseLine(vals[1:], value)
                return
        
        i = self.addProfile()
        self[i].ProfileName = vals[0]
        self[i]._parseLine(vals[1:], value)
        

PFList = None

def getProfileList(refresh=None):
    global PFList
    if PFList == None or refresh:
        PFList = ProfileList()
        PFList.load()
    return PFList

__author__ = "Harald Hoyer <harald@redhat.com>"
