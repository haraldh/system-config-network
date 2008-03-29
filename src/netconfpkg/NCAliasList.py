from netconfpkg import AliasList_base
import re

# pylint: disable-msg=W0232
class AliasList(AliasList_base):
    
    def test(self):
        from netconfpkg import NCHost
        for alias in self:
            if not NCHost.testHostname(alias):
                return False
        return True
