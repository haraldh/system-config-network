#!/usr/bin/python
import sys
import string
import os

if __name__ != '__main__':
    print "Usage: %s" % sys.argv[0]
    sys.exit(-1)

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

    if lines != str:
        return 1

import Conf

#
# test1
#
filename = "test1.out"
str = """
# testConfig file
a\tb
# comment
c\td
# comment2
"""
# read
writeConf(filename, str)
conf = Conf.Conf(filename)
os.unlink(filename)
# write
conf.write()
del conf
# check
if expectConf(filename, str):
    writeConf(filename + '.orig', str)
    print "Test1 failed!!!!"
    os.system("diff -u " + filename + " " + filename + ".orig")
    sys.exit(10)
# cleanup
os.unlink(filename)


#
# test2
#
filename = "test2.out"
str = """
# testConfig file
a=b
# comment
c=d
# comment2
"""
# read
writeConf(filename, str)
conf = Conf.ConfShellVar(filename)
os.unlink(filename)
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
a='e'
# comment
c='f'
# comment2
g=h
"""
if expectConf(filename, str):
    writeConf(filename + '.orig', str)
    print "Test2 failed!!!!"
    os.system("diff -u " + filename + " " + filename + ".orig")
    sys.exit(10)
# cleanup
os.unlink(filename)

#
# test3
#
filename = "test3.out"
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
writeConf(filename, str)
conf = Conf.ConfModules(filename)
os.unlink(filename)
# write
conf.write()
del conf
# check
if expectConf(filename, str):
    writeConf(filename + '.orig', str)
    print "Test1 failed!!!!"
    os.system("diff -u " + filename + " " + filename + ".orig")
    sys.exit(10)
# cleanup
os.unlink(filename)

#
# test4
#
filename = "test4.out"
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
writeConf(filename, str)
conf = Conf.ConfModules(filename)
os.unlink(filename)
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
if expectConf(filename, str):
    writeConf(filename + '.orig', str)
    print "Test2 failed!!!!"
    os.system("diff -u " + filename + " " + filename + ".orig")
    sys.exit(10)
# cleanup
os.unlink(filename)


sys.exit(0)
