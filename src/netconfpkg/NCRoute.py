from netconfpkg import Route_base
import re

# pylint: disable-msg=W0232

class Route(Route_base): 
    def testIP(self, value):
        ip_pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        if re.match(ip_pattern,value):
            return True
        else:
            return False
            
    def test(self):
        all_ok = self.testAddress(self.Address)
        all_ok &= self.testGateway(self.Gateway)
        all_ok &= self.testNetmask(self.Netmask)
        if not(all_ok):
            raise ValueError
        return True

    def testAddress(self, value):
        return self.testIP(value)

    def testGateway(self, value):
        if value == "":
            return True
        else: 
            return self.testIP(value)

    def testGatewayDevice(self, value):
        # check for consistency
        return True

    def testNetmask(self, value):
        # check for consistency
        if value == "":
            return True
        else: 
            return self.testIP(value)
