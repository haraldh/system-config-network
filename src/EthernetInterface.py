from InterfaceCreator import InterfaceCreator

class EthernetInterface (InterfaceCreator):
    def __init__ (self):
        pass

    def get_project_name (self):
        return "Ethernet"

    def get_project_description (self):
        return "Create a new ethernet connection.  The Ethernet interface is most typically used for a LAN or a DSL account.  This is a really lame description that should be fixed up later"

    def get_druid (self):
        pass

