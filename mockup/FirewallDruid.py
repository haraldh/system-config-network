import gnome.ui
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade
import CheckList

services = [
    ( "Web Server",
      "This allows people to access and view the web server on your computer. You do not need to enable this to view web pages elsewhere or to use the web server directly from the machine itself for things like developing pages.",
      80),
    ( "Incoming Mail",
      "Allow incoming SMTP mail delivery. You do not need to enable this if you collect your mail from your ISP's server by POP3 or IMAP, or if you use a tool such as fetchmail.",
      25),
    ( "Secure Shell",
      "Allow incoming secure shell access. This is an encrypted way to talk to your computer over the internet. You may also wish to read the ssh documentation and set up a list of hosts permitted to connect.",
      22),
    ( "Telnet",
      "Allow incoming telnet accesss. This allows access to the command line shell of the machine from outside, if you have a username and password. It is not encrypted and can therefore be spied upon. If possible avoid enabling this.",
      23)
    ]

class FirewallDruid:
    def __init__ (self, next_page):
        self.next_page = next_page
        self.xml = libglade.GladeXML ('firewall-druids.glade', 'druid')
        self.druids = []
        druid = self.xml.get_widget ('druid')
        for I in druid.children ():
            druid.remove (I)
            self.druids.append (I)

        self.xml.get_widget ('level_druid_page').connect ('next', self.on_level_druid_page_next)

        # Initialize values
        # page 1
        self.xml.get_widget ('high_security_radiobutton').set_active (FALSE)

        # page 2
        self.services_list = CheckList.CheckList ()
        for service in services:
            self.services_list.append_row (service[0], TRUE, service)
        self.xml.get_widget ('services_swindow').add (self.services_list)
        self.services_list.show ()
        self.services_list.connect ("select_row", self.on_services_list_select_row)
        self.services_list.select_row (0,0);

        # next page
        self.next_page.connect ("back", self.on_next_page_back)

    def get_druids (self):
        return self.druids

    def on_level_druid_page_next (self, druid_page, druid):
        if self.xml.get_widget ('custom_firewall_radiobutton').active:
            return FALSE
        print "FIXME! druid is garbage for some reason"
        #druid.set_page (self.next_page)
        return TRUE

    def on_services_list_select_row (self, clist, row, column, data):
        (val, service) = clist.get_row_data (row)
        self.xml.get_widget ('service_description_label').set_text (service[1])

    def on_next_page_back (self, druid_page, druid):
        print druid_page
        print druid
        if self.xml.get_widget ('custom_firewall_radiobutton').active:
            druid.set_page (self.druids[1])
        else:
            druid.set_page (self.druids[0])
        return TRUE

def get_firewall_pages (next_page):
    firewall = FirewallDruid (next_page)
    return firewall.get_druids ()

