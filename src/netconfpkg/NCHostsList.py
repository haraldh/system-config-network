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

from netconfpkg import HostsList_base, Host
import string

class HostsList(HostsList_base):
    def __init__(self,*args, **kwargs):
        HostsList_base.__init__(self, args, kwargs)

    def load(self, filename='/etc/hosts'):
        try:
            conffile = open(filename, 'r')
            lines = conffile.readlines()
            conffile.close()
        except:
            return
        num = 0
        for line in lines:
            line = line.strip()
            tmp = line.partition('#')
            comment = tmp[2]
            tmp = string.split(tmp[0])
            
            # if the line contains more than comment we suppose that it's ip with Aliases
            if len(tmp) > 0:
                entry = Host()
                entry.IP = tmp[0]
                entry.Hostname = tmp[1]
                entry.Comment = string.rstrip(comment)
                # FIXME add check if there is some alias!
                entry.createAliasList()
                if len(tmp) > 1:
                    for alias in tmp[2:]:
                        entry.AliasList.append(alias)
                entry.origLine = line
            else:
                entry = line

            # add every line to configuration
            self.append(entry)

    def __iter__(self):
        """Replace __iter__ for backwards compatibility. Returns only valid Host objects"""
#        return iter(filter(lambda x: isinstance(x, Host), HostsList_base.__iter__(self)))
        return iter([x for x in HostsList_base.__iter__(self) if isinstance(x, Host)])

    def save(self, **kwargs):
        if "filename" in kwargs:            
            conffile = open(kwargs["filename"],"w")
        elif "file" in kwargs:
            conffile = kwargs["file"]
        else:
            conffile = open("/etc/hosts", "w")

        for entry in HostsList_base.__iter__(self):
            if isinstance(entry, str):
                conffile.write(entry + "\n")
            elif isinstance(entry, Host):
                if not entry.changed and hasattr(entry, "origLine"):
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

if __name__ == '__main__':
    hlist = HostsList()
    hlist.load()
    print hlist
    hlist.save(file=sys.stdout)