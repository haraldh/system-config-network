#!/usr/bin/python
"""
Handle /etc/resolv.conf for various profiles
"""

NETCFGDIR="/etc/sysconfig/networking/"

import string

class ResolverFile:
    """
    A class for handing /etc/resolv.conf for various profiles
    """

    def __init__(self):
        """
        The initializer
        @self The object instance
        """
        self._servers=[]
        self._domains=[]

    def addDNSServer(self,server):
        """
        Add a DNSserver
        @self The object instance
        @server The server to add (IP)
        """
        
        if server in self._servers:  # Don't add the same server twice
            return
        if(len(self._servers)==3):
            raise RuntimeError("Max 3 DNS servers")
        self._servers.append(server)

    def deleteDNSServer(self,server):
        """
        Delete the given DNSServer
        @self The object instance
        @server The server to delete (IP)
        """
        self._servers.remove(server)

    def DNServers(self):
        """
        Return an array of the contained DNS servers
        @self The object instance
        """
        return self._servers

    def addSearchDomain(self,domain):
        """
        Add a domain to search for hosts to resolve
        @self The object instance
        @domain The domain to search
        """
        
        if domain in self._domains: # Don't add the same domain twice
            return
        if(len(self._domains)==6):
            raise RuntimeError("Max 6 search domains")
        self._domains.append(domain)

    def deleteSearchDomain(self,domain):
        """
        Delete a domain from the search list
        @self The object instance
        @domain The domain to delete
        """

        self._domains.remove(domain)

    def searchDomains(self):
        """
        Returns a list of domains to search in when resolving
        @self The object instance
        """

        return self._domains
        
    def toString(self):
        """
        Return a string representation of the object
        @self The object instance
        """
        res=""
        if(len(self._domains)>0):
            res=res+"search "
            for domain in self._domains:
                res=res+"%s " % (domain)
            res=res+"\n"
        for server in self._servers:
            res=res+"nameserver %s\n" % (server)
        return res

    def writeFile(self,filename):
        """
        Write the resolving info to a file
        @self The object instance
        @file The file to write to
        """

        text=self.toString()
        file=open(filename,"w")
        file.write(text)

    def writeProfile(self,profile="default"):
        """
        Write the host information to a profiled
        configuration file. The default profile is
        'default' (no shock there...)
        @self The object instance
        @profile The name of the profile
        """

        filename=NETCFGDIR+profile+"/resolv.conf"
        self.writeFile(filename)

    def readFile(self,filename):
        """
        Initialize the object with contents from a file
        @self The object instance
        @filename The name of the file to read
        """
        file=open(filename,"r")
        line=file.readline()
        while line:
            splits=string.split(line)
            if(len(splits)>0):
                if(splits[0]=="search"):
                    for domain in splits[1:]:
                        self.addSearchDomain(domain)
                if(splits[0]=="nameserver"):
                    for server in splits[1:]:
                        self.addDNSServer(server)
            line=file.readline()

    def readProfile(self,profile="default"):
        """
        Initialize the host information from a profiled
        configuration file.
        @self The object instance
        @profile The name of the profile
        """
        filename=NETCFGDIR+profile+"/resolv.conf"
        self.readFile(filename)
        
        
def test():
    """
    Some simple tests...
    """
    resfile=ResolverFile()
    resfile.addDNSServer("207.175.42.153")
    resfile.addDNSServer("207.175.43.111")
    resfile.addSearchDomain("devel.redhat.com")
    resfile.addDNSServer("127.0.0.1")
    resfile.addSearchDomain("redhat.com")
    resfile.deleteDNSServer("127.0.0.1")


if __name__ == "__main__":
    test()

