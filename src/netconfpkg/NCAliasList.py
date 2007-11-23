from netconfpkg import AliasList_base
import re

class AliasList(AliasList_base):
    
    def test(self):
        for alias in self:
            # hostname: names separated by '.' every name must be max 63 chars in length and the hostname max length is 255 chars
            if (len(alias) - alias.count('.')) < 256:
                names = alias.split('.')
                pattern = re.compile('([a-zA-Z]|[0-9])+(-[a-zA-Z]|-[0-9]|[a-zA-Z]|[0-9])*$')
                for name in names:
                   if len(name) < 63:
                       if not pattern.match(name):
                           return False
                return True
            else:
                return False
