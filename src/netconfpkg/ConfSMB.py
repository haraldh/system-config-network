# Copyright (C) 1997 Red Hat Software, Inc.
# Use of this software is subject to the terms of the GNU General
# Public License

# This module manages SMB configuration file handling
# These classes are available:
# ConfSMB(Conf):
#  Implements a dictionary of dictionaries of bools, ints, and strings.
#  Toplevel key is a string representing a share
#  Second level keys are literals representing config options.
#  Booleans are set and stored as 0/1, but read in the file as any legal
#  value, including (case insensitive) 0/false/no and 1/true/yes
#  So: turn off browsing home directories with
#     smb['homes']['browseable'] = 0

import sys
if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
from string import *
from regex import *
from Conf import *
import re
import os

# ConfSMB(Conf):
#  Implements a dictionary of dictionaries of bools, ints, and strings.
#  Toplevel key is a string representing a share
#  Second level keys are literals representing config options.
#  Booleans are set and stored as 0/1, but read in the file as any legal
#  value, including (case insensitive) 0/false/no and 1/true/yes
#  So: turn off browsing home directories with
#     smb['homes'][browseable] = 0
class ConfSMB(Conf):
    
    def __init__(self, filename='/etc/samba/smb.conf'):
        self.stanza_re = re.compile('^\s*\[(?P<stanza>[^\]]*)]\s*(?:;.*)?$', re.I)
        Conf.__init__(self, filename, '#;', '=', '=',
                      merge=1, create_if_missing=0)

    def read(self):
        Conf.read(self)
        self.initvars()
        
    def initvars(self):
        self.vars = {}
        self.rewind()
        stanza = None
        while 1:
            stanza = self.next_stanza()
            if not stanza:
                break
            self.vars[stanza] = {}
            
            self.nextline()
            while 1:
                vars = self.next_entry()
                if not vars:
                    break
                
                name = vars[0]
                value = vars[1]
                self.vars[stanza][name] = value
            
        self.rewind()

    def next_entry(self):
        while self.findnextline('^[\t ]*[\[A-Za-z_]+.*'):
            if self.is_stanza_decl():
                return 0
            vars = self.getfields()
            vars[1] = joinfields(vars[1:len(vars)], '=')
            
            self.nextline()
            
            if not vars:
                continue
            if len(vars) != 2:
                continue
            vars[0] = strip(vars[0])
            vars[1] = strip(vars[1])
            return vars        
            
        return 0
                
        
    def is_stanza_decl(self):
        # return true if the current line is of the form [...]
        if self.stanza_re.match(self.getline()):
            return 1
        return 0

    def find_stanza(self, stanza_name):
        # leave the current line at the first line of the stanza
        # (the first line after the [stanza_name] entry)
        self.rewind()
        while self.findnextline('^[\t ]*\[.*\]'):
            m = self.stanza_re.match(self.getline())

            if m and (stanza_name == m.group('stanza')):
                self.nextline()
                return 1
            
            self.nextline()
            
        self.rewind()
        return 0
                
    def next_stanza(self):
        # leave the current line at the first line of the stanza
        # (the first line after the [stanza_name] entry)
        while self.findnextline('^[\t ]*\[.*\]'):
            m = self.stanza_re.match(self.getline())
            if m:
                stanza = m.group('stanza')
                if stanza:
                    return stanza
                
            self.nextline()
            
        self.rewind()
        return 0
                

    def find_entry_in_current_stanza(self, entry_name):
        # leave the current line at the entry_name line or before
        # the [...] line of the next stanza (or the end of the file)
        # if entry_name does not exist.
        line = self.getline()
        if is_stanza_decl(line):
            self.line = self.line - 1
            return 0        
        
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return [[]]
        
    def __setitem__(self, varname, value):
        if len(value):
            self.vars[varname] = value
        self.rewind()
        for pair in value:
            if not self.findlinewithfield(2, varname):
                self.fsf()
                self.setfields([pair[0], varname, pair[1]])
        self.nextline()
        
        while self.findlinewithfield(2, varname):
            self.deleteline()
            
    def __delitem__(self, varname):
        del self.vars[varname]
        self.rewind()
        while self.findlinewithfield(2, varname):
            self.deleteline()
            
    def keys(self):
        # no need to return list in order here, I think.
        return self.vars.keys()
    
    def has_key(self, key):
        return self.vars.has_key(key)


if __name__ == '__main__':
    smb = ConfSMB()
    print smb.vars
    if smb.find_stanza("global"):
        print smb.getline()
    else:
        print "not found"
