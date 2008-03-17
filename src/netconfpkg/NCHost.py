"Host Module"

from netconfpkg import Host_base # pylint: disable-msg=E0611
import re
import socket

def testHostname(hostname):
    # hostname: names separated by '.' every name must be max 63 chars in length and the hostname max length is 255 chars
    if (len(hostname) - hostname.count('.')) < 256:
        names = hostname.split('.')
        # hostname with trailing dot
        if not names[-1]:
            names.pop()
        pattern = re.compile('([a-zA-Z]|[0-9])+(-[a-zA-Z]|-[0-9]|[a-zA-Z]|[0-9])*$')
        for name in names:
            if len(name) < 64:
                if not pattern.match(name):
                    return False
            else:
                return False
        return True
    else:
        return False

class Host(Host_base):
    HostID = None

    def __init__(self, *args, **kwargs):
        Host_base.__init__(self, *args, **kwargs)

    def testIP(self):
        try:
            socket.inet_pton(socket.AF_INET, self.IP) # pylint: disable-msg=E1101
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, self.IP) # pylint: disable-msg=E1101
            except socket.error:
                return False
        return True
    
    def testHostname(self):
        return testHostname(self.Hostname) # pylint: disable-msg=E1101
            
    def test(self):
        if not self.testIP():
            raise ValueError("IP")
        if not self.testHostname():
            raise ValueError("Hostname")
        if self.AliasList and not self.AliasList.test(): # pylint: disable-msg=E1101
            raise ValueError("Alias")
