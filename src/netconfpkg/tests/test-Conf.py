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
    print "Test1 failed"
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
a=e
# comment
c=f
# comment2
g=h
"""
if expectConf(filename, str):
    print "Test2 failed"
    sys.exit(10)
# cleanup
os.unlink(filename)
sys.exit(0)
