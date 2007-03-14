#!/usr/bin/python

import unittest
import sys
import string
import os

def writeConf(filename, str):
    try: os.unlink(filename)
    except OSError: pass
    file = open(filename, 'w', -1)
    file.write(str)
    file.close()

def expectConf(filename, str):
    if not os.path.isfile(filename):
        return 1

    file = open(filename, 'r', -1)
    lines = file.readlines()
    lines = string.join(lines, '')

    return (lines == str)

class TestConf(unittest.TestCase):
    filename = "test.out"
    def tearDown(self):
        try:
            os.unlink(self.filename)
        except: pass

    def testReadWrite(self):
        """Conf class: basic reading and writing"""
        str = """
# testConfig file
a\tb
# comment
c\td
# comment2
"""
        # read
        writeConf(self.filename, str)
        conf = Conf.Conf(self.filename)
        os.unlink(self.filename)
        # write
        conf.write()
        del conf
        # check
        if not expectConf(self.filename, str):
            writeConf(self.filename + '.orig', str)
            os.system("diff -u " + self.filename + " " + self.filename + ".orig")
            os.unlink(self.filename + '.orig')
            self.fail("Test1 failed!!!!")


    def testModify(self):
        """Conf class: reading, modify and writing"""
        str = """
# testConfig file
a=b
# comment
c=d
# comment2
"""
        # read
        writeConf(self.filename, str)
        conf = Conf.ConfShellVar(self.filename)
        os.unlink(self.filename)
        # modify
        conf["a"] = "e"
        conf["c"] = "f"
        conf["g"] = "h"
        # write
        conf.write()
        del conf
        # check
        str = """
# testConfig file
a=e
# comment
c=f
# comment2
g=h
"""
        if not expectConf(self.filename, str):
            writeConf(self.filename + '.orig', str)
            os.system("diff -u " + self.filename + " " + self.filename + ".orig")
            os.unlink(self.filename + '.orig')
            self.fail("Test2 failed!!!!")


    def testConfModules(self):
        """ConfModules class: basic reading and writing"""
        #
        # test3
        #
        str = """# Modules test file
alias parport_lowlevel parport_pc
#alias eth0 3c59x
alias eth3 3c59x
#alias eth0 3c59x
#alias sound-slot-1 emu10k1
alias sound-slot-0 emu10k1
#alias sound-slot-1 emu10k1
# comment comment
post-install sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
pre-remove sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -S >/dev/null 2>&1 || :alias usb-controller usb-uhci
post-install sound-slot-1 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
"""
        # read
        writeConf(self.filename, str)
        conf = Conf.ConfModules(self.filename)
        os.unlink(self.filename)
        # write
        conf.write()
        del conf
        # check
        if not expectConf(self.filename, str):
            writeConf(self.filename + '.orig', str)
            os.system("diff -u " + self.filename + " " + self.filename + ".orig")
            os.unlink(self.filename + '.orig')
            self.fail("Test3 failed!!!!")

    def testConfModulesModify(self):
        """ConfModules class: reading, modify and writing"""
        #
        # test4
        #
        str = """# Modules test file
alias parport_lowlevel parport_pc
#alias eth0 3c59x
alias eth3 3c59x
#alias eth0 3c59x
#alias sound-slot-1 emu10k1
alias sound-slot-0 emu10k1
#alias sound-slot-1 emu10k1
# comment comment
post-install sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
pre-remove sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -S >/dev/null 2>&1 || :alias usb-controller usb-uhci
post-install sound-slot-1 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
options parport_pc io=0x378 irq=7
options nsc-ircc io=0x02f8 dongle_id=0x09 irq=3 dma=0
options 3c59x debug=2
"""
        # read
        writeConf(self.filename, str)
        conf = Conf.ConfModules(self.filename)
        os.unlink(self.filename)
        # modify
        conf["eth3"]["alias"] = "3c59xaaa"
        conf["eth0"] = { "alias" : "3c59x" }
        # write
        conf.write()
        del conf
        # check
        str = """# Modules test file
alias parport_lowlevel parport_pc
#alias eth0 3c59x
alias eth3 3c59xaaa
#alias eth0 3c59x
#alias sound-slot-1 emu10k1
alias sound-slot-0 emu10k1
#alias sound-slot-1 emu10k1
# comment comment
post-install sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
pre-remove sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -S >/dev/null 2>&1 || :alias usb-controller usb-uhci
post-install sound-slot-1 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
options parport_pc io=0x378 irq=7
options nsc-ircc io=0x02f8 dongle_id=0x09 irq=3 dma=0
options 3c59x debug=2
alias eth0 3c59x
"""
        if not expectConf(self.filename, str):
            writeConf(self.filename + '.orig', str)
            os.system("diff -u " + self.filename + " " + self.filename + ".orig")
            os.unlink(self.filename + '.orig')
            self.fail("Test4 failed!!!!")

def suite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestConf,'test')
    return suite

if __name__ == "__main__":
    do_coverage = None
    if do_coverage:
        import coverage
        coverage.erase()
        coverage.start()

    from rhpl import Conf
    testRunner = unittest.TextTestRunner(verbosity=2)
    result = testRunner.run(suite())

    if do_coverage:
        coverage.stop()
        m = sys.modules.values()
        coverage.the_coverage.report(Conf, show_missing=0 )

    sys.exit(not result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/14 09:29:37 $"
__version__ = "$Revision: 1.13 $"
