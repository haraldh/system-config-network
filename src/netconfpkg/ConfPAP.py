## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Harald Hoyer <harald@redhat.com>

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

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

import Conf

class ConfPAP(Conf.Conf):
    beginline = '####### redhat-config-network will overwrite this part!!! (begin) ##########'
    endline = '####### redhat-config-network will overwrite this part!!! (end) ############'
    
    def __init__(self, filename):
        Conf.Conf.__init__(self, filename, '#', ' \t', ' \t')
        self.chmod(0600)

    def read(self):
        Conf.Conf.read(self)
        self.initvars()
        self.chmod(0600)

    def initvars(self):
        self.vars = {}
        self.beginlineplace = 0
        self.endlineplace = 0
        self.rewind()

        if not self.findnextline(self.beginline):
            #print "insertline"
            self.insertline(self.beginline)

        self.beginlineplace = self.tell()
        
        self.rewind()

        missing = 1
        while self.findnextline():
            if self.endline == self.getline():
                self.endlineplace = self.tell()
                missing = 0
                break
            self.nextline()
            
        if missing:
            self.insertline(self.endline)
            self.endlineplace = self.tell()

        self.seek(self.beginlineplace)

        while self.findnextcodeline():
            if self.tell() >= self.endlineplace:
                break
            # initialize dictionary of variable/name pairs
            # print self.getline()
            var = self.getfields()

            #if len(var[0]) and var[0][0] in '\'"':
            #    # found quote; strip from beginning and end
            #    quote = var[0][0]
            #    var[0] = var[0][1:]
            #    p = -1
            #    try:
            #        while cmp(var[0][p], quote):
            #            # ignore whitespace, etc.
            #            p = p - 1
            #    except:
            #        raise IndexError, 'end quote not found in '+self.filename+':'+var[0]
            #    var[0] = var[0][:p]
                
            if var and (len(var) == 3):
                self.vars[var[0]] = var[2]
            
            self.nextline()
            
        self.rewind()

    def insertline(self, line=''):
        place = self.tell()
        if place < self.beginlineplace:
            self.beginlineplace = self.beginlineplace + 1
            
        if place < self.endlineplace:
            self.endlineplace = self.endlineplace + 1
            
        self.lines.insert(self.line, line)

    def deleteline(self):
        place = self.tell()
        self.lines[self.line:self.line+1] = []
        
        if place < self.beginlineplace:
            self.beginlineplace = self.beginlineplace -1
            
        if place < self.endlineplace:
            self.endlineplace = self.endlineplace - 1

    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return ''

    def __setitem__(self, varname, value):
        place=self.tell()
        self.seek(self.beginlineplace)
        missing=1
        if len(varname) == 2:
            login = '\"' + varname[0] + '\"'
            server = varname[1]
        else:
            login = '\"' + varname + '\"'
            if len(value) == 2:
                server = value[0]
                value = value[1]
            else:
                server = '*'                
            
        while self.findnextcodeline():
            if self.tell() >= self.endlineplace:
                break

            var = self.getfields()
            
            if var and (len(var) == 3):                
                if login == var[0] and server == var[1]:
                        self.setfields([ login, server, value ] )
                        missing=0
            self.nextline()
            
        if missing:
            self.seek(self.endlineplace)
            self.insertlinelist([ login, server, value ] )
                
        self.vars[login] = value

    def __delitem__(self, varname):
        # delete *every* instance...
        self.seek(self.beginlineplace)
        if len(varname) == 2:
            login = varname[0]
            server = varname[1]
        else:
            login = varname
            server = None        

        while self.findnextcodeline():
            if self.tell() >= self.endlineplace:
                break

            var = self.getfields()
            
            if var and (len(var) == 3):                
                if login == var[0] and (not server or server == var[1]):
                    self.deleteline()
            self.nextline()
                    
        if self.vars.has_key(varname):
            del self.vars[varname]
            
    def has_key(self, key):
        if self.vars.has_key(key): return 1
        return 0
    
    def keys(self):
        return self.vars.keys()        

if __name__ == '__main__':
    pap = ConfPAP("/etc/ppp/pap-secrets")
    for key in pap.keys():
        print key + ' ' + str(pap[key])
        del pap[key]
        
    pap['test1'] = 'pappasswd1'
    pap['test2'] = 'pappasswd2'
    pap['test3'] = 'pappasswd3'

    print pap.lines

    pap.write()

