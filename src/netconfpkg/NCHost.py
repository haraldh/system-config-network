from netconfpkg import Host_base, AliasList
#import AliasList
import socket
import re

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
    def testIP(self):
            try:
                socket.inet_pton(socket.AF_INET, self.IP)
            except socket.error:
                try:
                    socket.inet_pton(socket.AF_INET6, self.IP)
                except:
                    return False
            return True
    
    def testHostname(self):
        return testHostname(self.Hostname)
        
    def testAliasList(self):
        return self.AliasList.test()
    
    def test(self):
        if not self.testIP():
            raise ValueError("IP")
        if not self.testHostname():
            raise ValueError("Hostname")
        if not self.testAliasList():
            raise ValueError("Alias")
