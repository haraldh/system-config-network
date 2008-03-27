from netconfpkg.NC_functions import testHostname
from netconfpkg.gdt import (Gdtstr, Gdtlist)


class Alias(Gdtstr):
    "Alias of a Host"

class AliasList_base(Gdtlist):
    "List of aliases"

class AliasList(AliasList_base):        
    def test(self):
        for alias in self:
            if not testHostname(alias):
                return False
        return True
