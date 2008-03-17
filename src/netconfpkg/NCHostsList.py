## Copyright (C) 2001-2007 Red Hat, Inc.

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

if __name__ == '__main__':
    import sys
    sys.path.append("../")
    sys.path.append("./")

from netconfpkg import HostsList_base # pylint: disable-msg=E0611
from netconfpkg.NCHost import Host

class HostsList(HostsList_base):
    def __init__(self, *args, **kwargs):
        HostsList_base.__init__(self, *args, **kwargs)
    
    def test(self):
        error = None
        num = 0
        for host in self:
            num += 1
            if isinstance(host, Host):
                try:
                    host.test()
                except ValueError, e:
                    if not error:
                        error = "Error in hostslist\nWrong: %s in entry %i" % (e.message, num)
                    else:
                        error += "Wrong: %s in entry %i" % (e.message, num)
        if error:
            raise ValueError(error)
    
    def load(self, filename='/etc/hosts'):
        try:
            conffile = open(filename, 'r')
            lines = conffile.readlines()
            conffile.close()
        except:
            return
        num = 0
        error = None
        badlines = []
        for line in lines:
            num += 1
            line = line.strip()
            tmp = line.partition('#')
            comment = tmp[2]
            tmp = tmp[0].split()
            
            # if the line contains more than comment we suppose that it's ip with Aliases
            if len(tmp) > 0:
                entry = Host()
                entry.IP = tmp[0]
                entry.Comment = comment.rstrip()
                entry.createAliasList() # pylint: disable-msg=E1101
                if len(tmp) > 1:
                    entry.Hostname = tmp[1]
                    for alias in tmp[2:]:
                        entry.AliasList.append(alias) # pylint: disable-msg=E1101
                entry.origLine = line
                # catch invalid entry in /etc/hosts
                try:
                    entry.test()
                except ValueError, e:
                    badlines.append((num, e.message))
                    if not error:
                        error = "Error while parsing /etc/hosts:\nWrong %s on line %i\n" % (e.message, num)                    
                    else:
                        error += "Wrong %s on line %i\n" % (e.message, num)
            else:
                entry = line

            # add every line to configuration
            self.append(entry) # pylint: disable-msg=E1101
        if error:
            e = ValueError(error)
            e.badlines = badlines
            raise e

    def __iter__(self):
        """Replace __iter__ for backwards compatibility. Returns only valid Host objects"""
#        return iter(filter(lambda x: isinstance(x, Host), HostsList_base.__iter__(self)))
        return iter([x for x in HostsList_base.__iter__(self) if isinstance(x, Host)])

    def save(self, **kwargs):
        if "filename" in kwargs:            
            conffile = open(kwargs["filename"], "w")
        elif "file" in kwargs:
            conffile = kwargs["file"]
        else:
            conffile = open("/etc/hosts", "w")

        for entry in HostsList_base.__iter__(self):
            if isinstance(entry, str):
                conffile.write(entry + "\n")
            elif isinstance(entry, Host):
                if (not entry.changed) and hasattr(entry, "origLine"):
                    conffile.write(entry.origLine+"\n")
                    continue
                if entry.IP:
                    conffile.write(entry.IP)
                if entry.Hostname:
                    conffile.write("\t" + entry.Hostname)
                if entry.AliasList:
                    for alias in entry.AliasList:
                        conffile.write("\t" + alias)
                if hasattr(entry, "Comment") and entry.Comment:
                    conffile.write(" #" + entry.Comment)

                conffile.write("\n")

        if not "file" in kwargs:
            conffile.close()

    def _parseLine(self, vals, value):
        for host in self:
            if host.HostID == vals[0]:
                host._parseLine(vals[1:], value) # pylint: disable-msg=W0212
                return
        i = self.addHost() # pylint: disable-msg=E1101
        self[i].HostID = vals[0]
        self[i]._parseLine(vals[1:], value) # pylint: disable-msg=W0212

if __name__ == '__main__':
    hlist = HostsList()
    hlist.load()
    print hlist
    hlist.save(file=sys.stdout)
