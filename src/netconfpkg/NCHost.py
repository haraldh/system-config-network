from netconfpkg import Host_base, AliasList
#import AliasList
import socket
import re

class Host(Host_base):
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
        # hostname: names separated by '.' every name must be max 63 chars in length and the hostname max length is 255 chars
        if (len(self.Hostname) - self.Hostname.count('.')) < 256:
            names = self.Hostname.split('.')
            pattern = re.compile('([a-zA-Z]|[0-9])+(-[a-zA-Z]|-[0-9]|[a-zA-Z]|[0-9])*$')
            for name in names:
               if len(name) < 63:
                   if not pattern.match(name):
                       return False
            return True
        else:
            return False
    
    def testAliasList(self):
        return self.AliasList.test()
    
    def test(self):
        # how to use automatical call and catch exceptions?
        message = ""
        if not self.testIP():
            raise ValueError("IP")
        if not self.testHostname():
            raise ValueError("Hostname")
        if not self.testAliasList():
            raise ValueError("Alias")
