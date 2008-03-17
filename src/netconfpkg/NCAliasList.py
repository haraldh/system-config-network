from netconfpkg import AliasList_base # pylint: disable-msg=E0611
from netconfpkg import NCHost

class AliasList(AliasList_base):
    def __init__(self, *args, **kwargs):
        AliasList_base.__init__(self, *args, **kwargs)
        
    def test(self):
        for alias in self:
            if not NCHost.testHostname(alias):
                return False
        return True
