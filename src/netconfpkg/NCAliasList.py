from netconfpkg.NC_functions import testHostname
from netconfpkg.gdt import (Gdtstr, Gdtlist)


class Alias(Gdtstr):
    "Alias of a Host"
    
class AliasList(Gdtlist):        
    "List of aliases"
    def test(self):
        for alias in self:
            if not testHostname(alias):
                return False
        return True
