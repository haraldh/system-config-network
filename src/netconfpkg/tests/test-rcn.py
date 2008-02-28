#!/usr/bin/python
# -*- coding: utf-8 -*-

True = (1==1)
False = not True

import unittest
import sys
import string
import os


sys.path.append(os.getcwd() + "/../../")

if os.environ.has_key("srcdir"):
    srcdir = os.environ["srcdir"]
    sys.path.append(srcdir + "/../../")
else:
    srcdir = os.getcwd()


CHROOT = os.path.abspath(os.getcwd()) + "/./rcntest-root"

BASICSETUP="""DeviceList.Ethernet.eth0.Type=Ethernet
DeviceList.Ethernet.eth0.BootProto=dhcp
DeviceList.Ethernet.eth0.Device=eth0
DeviceList.Ethernet.eth0.OnBoot=True
DeviceList.Ethernet.eth0.DeviceId=eth0
ProfileList.default.ActiveDevices.1=eth0
ProfileList.default.HostsList.1.IP=127.0.0.1
ProfileList.default.HostsList.1.Hostname=localhost.localdomain
ProfileList.default.HostsList.1.AliasList.1=localhost
ProfileList.default.HostsList.2.AliasList.1=localhost6
ProfileList.default.HostsList.2.Hostname=localhost6.localdomain6
ProfileList.default.HostsList.2.IP=::1
ProfileList.default.HostsList.3.AliasList.1=test1
ProfileList.default.HostsList.3.AliasList.2=test2
ProfileList.default.HostsList.3.Hostname=test
ProfileList.default.HostsList.3.IP=10.1.1.1
ProfileList.default.DNS.SecondaryDNS=172.16.2.15
ProfileList.default.DNS.SearchList.1=stuttgart.redhat.com
ProfileList.default.DNS.SearchList.2=devel.redhat.com
ProfileList.default.DNS.SearchList.3=redhat.com
ProfileList.default.DNS.Domainname=
ProfileList.default.DNS.Hostname=jever.stuttgart.redhat.com
ProfileList.default.DNS.TertiaryDNS=
ProfileList.default.DNS.PrimaryDNS=172.16.2.2
ProfileList.default.Active=True
ProfileList.default.ProfileName=default
"""

def writeConf(filename, str):
    try: os.unlink(filename)
    except OSError: pass
    file = open(filename, 'w+', -1)
    file.write(str)
    file.close()

def sortStr(str):
    str = string.split(str, '\n')
    str.sort()
    #str = string.join(str, '\n')
    while str[0] == "":
        str = str[1:]
    return str


def expectConf(fileorlines, str):
    if os.path.isfile(fileorlines):
        file = open(fileorlines, 'r', -1)
        lines = file.readlines()
        lines.sort()
        for i in xrange(len(lines)):
            if lines[i][-1:] == "\n":
                lines[i] = lines[i][:-1]

    else:
        lines = sortStr(fileorlines)

    str = string.split(str, '\n')
    str.sort()
    #str = string.join(str, '\n')
    if str[0] == "":
        str = str[1:]

    l = min(len(lines), len(str))

    for i in xrange(l):
        if (lines[i] != str[i]):
            print "\n- %s\n+ %s\n" % (str[i], lines[i])
            break
    else:
        return True

    print string.join(lines, "\n")
    return False



class TestRCN(unittest.TestCase):
    def setupChroot(self):
        cmd = "[ -d '%s' ] && rm -fr '%s'" % (CHROOT, CHROOT)
        #print cmd
        #sys.stdout.flush()
        os.system(cmd)
        cmd = "mkdir '%s'; cp -ar '%s/etc' '%s';chmod -R ug+rw %s" % (CHROOT, srcdir, CHROOT, CHROOT)
        #print cmd
        #sys.stdout.flush()
        os.system(cmd)


    def setUp(self):
        self.oldstderr = sys.stderr
        self.oldstdout = sys.stdout


    def tearDown(self):
        sys.stderr = self.oldstderr
        sys.stdout = self.oldstdout
        try:
            #os.unlink("stderr")
            #os.unlink("stdout")
            pass
        except:
            pass

    def getConf(self):
        PROGNAME='system-config-network'
        from netconfpkg import NC_functions
        NC_functions.prepareRoot(CHROOT)

        from netconfpkg import \
             NCDeviceList, NCProfileList, \
             NCHardwareList, NCIPsecList

        from netconfpkg.NC_functions import log

        NC_functions.setVerboseLevel(100)
        NC_functions.setDebugLevel(100)
        log.set_loglevel(NC_functions.getVerboseLevel())

        devlists = [
#            NCHardwareList.getHardwareList(),
#            NCIPsecList.getIPsecList(),
            NCDeviceList.getDeviceList(),
            NCProfileList.getProfileList(),
            ]

        devstr = ""
        for devlist in devlists:
            devlist.load()
            devstr +=  str(devlist)
        return devstr

    def redirectStd(self):
        sys.stderr.flush()
        sys.stdout.flush()
        self.oldstderr = sys.stderr
        self.oldstdout = sys.stdout
        sys.stdout = open("stdout", "w")
        sys.stderr = open("stderr", "w")
        from netconfpkg.NC_functions import log
        log.open()

    def redirectEnd(self):
        sys.stderr.close()
        sys.stdout.close()
        sys.stderr = self.oldstderr
        sys.stdout = self.oldstdout
        from netconfpkg.NC_functions import log
        log.open()

    def test00Basic(self):
        """Testing basic reading from a chroot setup with network-cmd"""
        self.setupChroot()
        self.redirectStd()
        import netconf_cmd
        cmdline = [ "-d", "-o", "--root=" + CHROOT ]
        netconf_cmd.main(cmdline)
        expect = BASICSETUP
        self.redirectEnd()
        self.failUnless(expectConf("stdout", expect))

    def test01Read(self):
        """Test manual reading"""
        self.setupChroot()
        self.redirectStd()
        from netconfpkg import NC_functions
        NC_functions.prepareRoot(CHROOT)
        NC_functions.updateNetworkScripts(True)
        devstr = self.getConf()
        expect = BASICSETUP
        self.redirectEnd()
        self.failUnless(expectConf(expect, devstr))

    def test02Profile(self):
        """Test profile creation """
        #self.clearModules()
        self.test01Read()
        self.redirectStd()
        from netconfpkg import NC_functions, \
             NCDeviceList, NCProfileList, \
             NCHardwareList, NCIPsecList

        profilelist = NCProfileList.getProfileList()

        text = "newprofile"
        i = profilelist.addProfile()
        prof = profilelist[i]
        prof.apply(profilelist[0])
        prof.ProfileName = text
        prof.commit()

        profilelist.switchToProfile(prof, dochange = True)

        self.save()

        devstr = self.getConf()
        expect = """DeviceList.Ethernet.eth0.BootProto=dhcp
DeviceList.Ethernet.eth0.Device=eth0
DeviceList.Ethernet.eth0.DeviceId=eth0
DeviceList.Ethernet.eth0.OnBoot=True
DeviceList.Ethernet.eth0.Type=Ethernet
ProfileList.default.Active=False
ProfileList.default.ActiveDevices.1=eth0
ProfileList.default.DNS.Domainname=
ProfileList.default.DNS.Hostname=jever.stuttgart.redhat.com
ProfileList.default.DNS.PrimaryDNS=172.16.2.2
ProfileList.default.DNS.SearchList.1=stuttgart.redhat.com
ProfileList.default.DNS.SearchList.2=devel.redhat.com
ProfileList.default.DNS.SearchList.3=redhat.com
ProfileList.default.DNS.SecondaryDNS=172.16.2.15
ProfileList.default.DNS.TertiaryDNS=
ProfileList.default.HostsList.1.AliasList.1=localhost
ProfileList.default.HostsList.1.Hostname=localhost.localdomain
ProfileList.default.HostsList.1.IP=127.0.0.1
ProfileList.default.HostsList.2.AliasList.1=localhost6
ProfileList.default.HostsList.2.Hostname=localhost6.localdomain6
ProfileList.default.HostsList.2.IP=::1
ProfileList.default.HostsList.3.AliasList.1=test1
ProfileList.default.HostsList.3.AliasList.2=test2
ProfileList.default.HostsList.3.Hostname=test
ProfileList.default.HostsList.3.IP=10.1.1.1
ProfileList.default.ProfileName=default
ProfileList.newprofile.Active=True
ProfileList.newprofile.ActiveDevices.1=eth0
ProfileList.newprofile.DNS.Domainname=
ProfileList.newprofile.DNS.Hostname=jever.stuttgart.redhat.com
ProfileList.newprofile.DNS.PrimaryDNS=172.16.2.2
ProfileList.newprofile.DNS.SearchList.1=stuttgart.redhat.com
ProfileList.newprofile.DNS.SearchList.2=devel.redhat.com
ProfileList.newprofile.DNS.SearchList.3=redhat.com
ProfileList.newprofile.DNS.SecondaryDNS=172.16.2.15
ProfileList.newprofile.DNS.TertiaryDNS=
ProfileList.newprofile.HostsList.1.AliasList.1=localhost
ProfileList.newprofile.HostsList.1.Hostname=localhost.localdomain
ProfileList.newprofile.HostsList.1.IP=127.0.0.1
ProfileList.newprofile.HostsList.2.AliasList.1=localhost6
ProfileList.newprofile.HostsList.2.Hostname=localhost6.localdomain6
ProfileList.newprofile.HostsList.2.IP=::1
ProfileList.newprofile.HostsList.3.AliasList.1=test1
ProfileList.newprofile.HostsList.3.AliasList.2=test2
ProfileList.newprofile.HostsList.3.Hostname=test
ProfileList.newprofile.HostsList.3.IP=10.1.1.1
ProfileList.newprofile.ProfileName=newprofile
"""
        self.redirectEnd()

        self.failUnless(expectConf(devstr, expect))

    def test03Profile(self):
        """Test profile removal"""
        self.redirectStd()
        from netconfpkg import NC_functions
        NC_functions.prepareRoot(CHROOT)
        devstr = self.getConf()

        from netconfpkg import  \
             NCDeviceList, NCProfileList, \
             NCHardwareList, NCIPsecList

        from netconfpkg.NC_functions import log
        profilelist = NCProfileList.getProfileList()
        NC_functions.setVerboseLevel(100)
        NC_functions.setDebugLevel(100)
        log.set_loglevel(NC_functions.getVerboseLevel())

        profilelist.remove(profilelist.getActiveProfile())
        profilelist.switchToProfile('default')
        profilelist.commit()
        self.save()
        NC_functions.setVerboseLevel(0)
        NC_functions.setDebugLevel(0)
        devstr = self.getConf()
        self.redirectEnd()
        expect = BASICSETUP
        self.failUnless(expectConf(expect, devstr))

    def save(self):
        from netconfpkg import NCProfileList
        profilelist = NCProfileList.getProfileList()
        profilelist.fixInterfaces()
        self.saveHardware()
        self.saveDevices()
        self.saveIPsecs()
        self.saveProfiles()

    def saveDevices(self):
        from netconfpkg import NCDeviceList
        devicelist = NCDeviceList.getDeviceList()
        devicelist.save()
        devicelist.setChanged(False)

    def saveHardware(self):
        from netconfpkg import NCHardwareList
        hardwarelist = NCHardwareList.getHardwareList()
        hardwarelist.save()
        hardwarelist.setChanged(False)

    def saveProfiles(self):
        from netconfpkg import NCProfileList
        profilelist = NCProfileList.getProfileList()
        profilelist.save()
        profilelist.setChanged(False)

    def saveIPsecs(self):
        from netconfpkg import NCIPsecList
        ipseclist = NCIPsecList.getIPsecList()
        ipseclist.save()
        ipseclist.setChanged(False)


# FIXME: check [165543] system-config-network-cmd - incorrect profile import - hosts file
# FIXME: check [165536] TB /usr/lib/python2.3/string.py:135:join:TypeError: sequence expected, NoneType found

def suite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestRCN,'test')
    return suite

if __name__ == "__main__":
    docoverage = False
    #docoverage = True
    if docoverage:
        import coverage
        coverage.erase()
        coverage.start()
    #import netconf_cmd
    #import netconfpkg
    testRunner = unittest.TextTestRunner(verbosity=2)
    result = testRunner.run(suite())
    if docoverage:
        coverage.stop()
        m = []
        keys = []
        keys.extend(sys.modules.keys())
        keys.sort()
        for key in keys:
            try:
                path = sys.modules[key].__file__
            except:
                path = ""
            if path.find(".py") == -1:
                continue
            if key.find("netconfpkg") != -1:
                m.append(sys.modules[key])
#            elif key.find("rhpl") != -1:
#                m.append(sys.modules[key])

        coverage.the_coverage.report(m, show_missing=0 )
        coverage.the_coverage.annotate(m, os.getcwd())
    #coverage.the_coverage.report(netconfpkg.NC_functions, show_missing=0 )
    #print sys.modules.keys()
    os.system("rm -fr %s" % CHROOT)

    sys.exit(not result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/14 13:39:43 $"
__version__ = "$Revision: 1.10 $"
