from InterfaceCreator import InterfaceCreator
import libglade
import FirewallDruid

class DialupInterface (InterfaceCreator):
    def __init__ (self):
        pass

    def get_project_name (self):
        return "Dialup connection"

    def get_project_description (self):
        return "Create a new dialup connection.  The dialup interface is used primarily for connecting to an ISP over a modem.  This is a really lame description that should be fixed up later"

    def get_druids (self):
        self.xml = libglade.GladeXML('dialup.glade', 'druid')
        retval = []
        druid = self.xml.get_widget ('druid')
        for I in druid.children ():
            druid.remove (I)
            retval.append (I)

        return retval[0:2] + FirewallDruid.get_firewall_pages (retval[2]) + retval[2:]

